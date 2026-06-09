import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("OLLAMA_API_KEY"),
    reason="OLLAMA_API_KEY not set",
)

DESCRIPTION = "Woman sitting at a café table staring at a laptop with an empty coffee cup beside her."


def test_story_idea_returns_four_ideas():
    from agent_flow.agents.story_idea_agent import StoryIdeaAgent

    agent = StoryIdeaAgent()
    ideas = agent.run(DESCRIPTION, genres=["realistic"])

    assert isinstance(ideas, list)
    assert len(ideas) == 10
    assert all(isinstance(i, str) and i for i in ideas)
