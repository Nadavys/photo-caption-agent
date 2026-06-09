import logging
import time

from agent_flow.agents.base import BaseAgent
from agent_flow.parsing import parse_completions
from agent_flow.prompts.refinement import SYSTEM_PROMPT as _SYSTEM_PROMPT
from agent_flow.refinement_context import RefinementContext

log = logging.getLogger(__name__)


class RefinementAgent(BaseAgent):
    def run(self, ctx: RefinementContext) -> list[str]:
        if not ctx.iterations:
            raise ValueError("RefinementContext must have at least one iteration.")
        log.info(
            "[refine] start — rounds=%d latest_instruction=%r",
            len(ctx.iterations),
            ctx.iterations[-1].instruction,
        )
        completions = self._generate(ctx)
        log.info("[refine] done — %d completions", len(completions))
        return completions

    def _generate(self, ctx: RefinementContext) -> list[str]:
        last = ctx.iterations[-1]
        selected = last.completions[last.selected_index]

        genre_line = ""
        if ctx.original_genres:
            names = ", ".join(ctx.original_genres)
            genre_line = f"Genre styles: {names}\n\n"

        story_line = f"Story context: {ctx.story_idea}\n\n" if ctx.story_idea else ""
        user_content = (
            f"Original description: {ctx.original_description}\n\n"
            f"{genre_line}"
            f"{story_line}"
            f"Selected completion:\n\"{selected}\"\n\n"
            f"Instruction: {last.instruction}"
        )
        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]

        log.info("[refine] model=%s temperature=%.1f messages=%d", self._model, self._temperature, len(messages))
        t0 = time.monotonic()
        response = self._client.chat(
            model=self._model,
            messages=messages,
            options={"temperature": self._temperature},
        )
        elapsed = time.monotonic() - t0
        content = response.message.content
        if not content:
            raise ValueError("Model returned an empty response.")
        raw = content.strip()
        log.info("[refine] raw response (%.2fs):\n%s", elapsed, raw)
        completions = parse_completions(raw, expected=5)
        for i, c in enumerate(completions, 1):
            log.info("[refine] completion %d: %s", i, c)
        return completions
