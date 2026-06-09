import logging
import time

from agent_flow.agents.base import BaseAgent
from agent_flow.genres import GENRES, build_genre_lines
from agent_flow.parsing import parse_story_ideas
from agent_flow.prompts.story_ideas import SYSTEM_PROMPT as _SYSTEM_PROMPT

log = logging.getLogger(__name__)


class StoryIdeaAgent(BaseAgent):
    def run(self, description: str, genres: list[str] | None = None, exclude: list[str] | None = None) -> list[str]:
        log.info("[story-idea] start — description: %r genres=%s exclude=%d", description, genres or [], len(exclude or []))
        ideas = self._generate(description, genres, exclude or [])
        log.info("[story-idea] done — %d ideas", len(ideas))
        return ideas

    def _generate(self, description: str, genres: list[str] | None, exclude: list[str]) -> list[str]:
        log.info("[story-idea] model=%s temperature=%.1f", self._model, self._temperature)
        user_content = description
        if exclude:
            prior = "\n".join(f"{i + 1}. {idea}" for i, idea in enumerate(exclude))
            user_content = f"{description}\n\nIdeas so far — generate 10 new ones, do not repeat these:\n{prior}"
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
        log.info("[story-idea] raw response (%.2fs):\n%s", elapsed, raw)
        ideas = parse_story_ideas(raw, expected=10)
        for i, idea in enumerate(ideas, 1):
            log.info("[story-idea] idea %d: %s", i, idea)
        return ideas

    def _build_system_prompt(self, genres: list[str] | None) -> str:
        if not genres:
            return _SYSTEM_PROMPT.format(genre_block="")
        lines = build_genre_lines(genres)
        genre_block = f"\n* Genre style(s) to consider:\n{lines}\nLet these shape the emotional tone of the ideas."
        return _SYSTEM_PROMPT.format(genre_block=genre_block)
