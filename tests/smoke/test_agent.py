import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("OLLAMA_API_KEY"),
    reason="OLLAMA_API_KEY not set",
)


USER_INPUT = "Woman standing in front of a bakery display case looking at a tray of fresh pastries, holding a wallet in her hand"
USER_INPUT = "* Woman sitting at a café table staring at a laptop with an empty coffee cup beside her."

def test_run_returns_results():
    from agent_flow.agents.dialogue_completion_agent import DialogueCompletionAgent
    agent = DialogueCompletionAgent()
    run = agent.run
    results = run(
        USER_INPUT,
        genres=["romantic", "realistic"],
    )
    assert isinstance(results, list)
    assert len(results) > 0



