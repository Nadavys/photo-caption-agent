import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("OLLAMA_API_KEY"),
    reason="OLLAMA_API_KEY not set",
)

_TEST_IMAGE = Path(__file__).parents[2] / "images" / "public-domain-image.jpeg"


@pytest.mark.skipif(not _TEST_IMAGE.exists(), reason="test image not found")
def test_vision_agent_returns_description():
    from agent_flow.agents.vision_agent import VisionAgent

    agent = VisionAgent()
    description = agent.describe(str(_TEST_IMAGE))

    assert isinstance(description, str)
    assert len(description) > 0


def test_vision_agent_rejects_missing_file():
    from agent_flow.agents.vision_agent import VisionAgent

    agent = VisionAgent()
    with pytest.raises(ValueError, match="Image file not found"):
        agent.describe("/nonexistent/path/photo.jpg")


def test_vision_agent_rejects_unsupported_format(tmp_path):
    from agent_flow.agents.vision_agent import VisionAgent

    bad_file = tmp_path / "photo.bmp"
    bad_file.write_bytes(b"BM")
    agent = VisionAgent()
    with pytest.raises(ValueError, match="Unsupported image format"):
        agent.describe(str(bad_file))
