import logging
import time

from agent_flow.agents.base import BaseAgent
from agent_flow.genres import build_genre_lines
from agent_flow.parsing import parse_completions
from agent_flow.prompts.dialogue import SYSTEM_PROMPT as _SYSTEM_PROMPT

log = logging.getLogger(__name__)


class DialogueCompletionAgent(BaseAgent):
    def run(self, description: str, genres: list[str] | None = None, story_idea: str | None = None) -> list[str]:
        log.info("[agent] start — description: %r genres=%s story_idea=%r", description, genres or [], story_idea)
        completions = self._generate_completions(description, genres, story_idea)
        log.info("[agent] done — %d completions", len(completions))
        return completions

    def _generate_completions(self, description: str, genres: list[str] | None = None, story_idea: str | None = None) -> list[str]:
        log.info("[agent] model=%s temperature=%.1f genres=%s", self._model, self._temperature, genres or [])
        log.info("[agent] input: %r story_idea=%r", description, story_idea)
        user_content = description
        if story_idea:
            user_content = f"{description}\n\nStory context: {story_idea}"
        t0 = time.monotonic()
        response = self._client.chat(
            model=self._model,
            messages=[
                {"role": "system", "content": self._build_system_prompt(genres)},
                {"role": "user", "content": user_content},
            ],
            options={"temperature": self._temperature},
        )
        elapsed = time.monotonic() - t0
        content = response.message.content
        if not content:
            raise ValueError("Model returned an empty response.")
        raw = content.strip()
        log.info("[agent] raw response (%.2fs):\n%s", elapsed, raw)
        completions = parse_completions(raw, expected=4)
        for i, c in enumerate(completions, 1):
            log.info("[agent] completion %d: %s", i, c)
        return completions

    def _build_system_prompt(self, genres: list[str] | None) -> str:
        if not genres:
            return _SYSTEM_PROMPT.format(genre_block="")
        lines = build_genre_lines(genres)
        genre_block = f"\n\nGenre style(s) to apply across all 4 completions:\n{lines}\nLet these styles shape tone, word choice, and emotional register while keeping each perspective distinct."
        return _SYSTEM_PROMPT.format(genre_block=genre_block)
