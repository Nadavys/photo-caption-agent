import logging
import os
import time
from pathlib import Path

from agent_flow.agents.base import BaseAgent

log = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

_PROMPT = (
    "Describe this photo in 1–3 plain-text sentences. "
    "Focus on the people, setting, mood, and action. "
    "No commentary — just describe what you see."
)


class VisionAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__()
        self._model = os.environ.get("OLLAMA_VISION_MODEL") or self._model

    def describe(self, image_path: str) -> str:
        path = Path(image_path).expanduser().resolve()
        if not path.exists():
            raise ValueError(f"Image file not found: {path}")
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError("Unsupported image format. Use JPEG, PNG, WEBP, or GIF.")

        log.info("[vision] model=%s path=%s", self._model, image_path)
        t0 = time.monotonic()
        response = self._client.chat(
            model=self._model,
            messages=[
                {
                    "role": "user",
                    "content": _PROMPT,
                    "images": [path.read_bytes()],
                }
            ],
        )
        elapsed = time.monotonic() - t0
        content = response.message.content
        if not content:
            raise ValueError("Vision model returned an empty response.")
        description = content.strip()
        log.info("[vision] done (%.2fs): %r", elapsed, description)
        return description
