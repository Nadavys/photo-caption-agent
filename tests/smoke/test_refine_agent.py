import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("OLLAMA_API_KEY"),
    reason="OLLAMA_API_KEY not set",
)

DESCRIPTION = "Woman sitting at a café table staring at a laptop with an empty coffee cup beside her."


def test_refine_returns_five_completions():
    from agent_flow.agents.dialogue_completion_agent import DialogueCompletionAgent
    from agent_flow.agents.refinement_agent import RefinementAgent
    from agent_flow.refinement_context import RefinementContext, RefinementIteration

    base = DialogueCompletionAgent()
    round0 = base.run(DESCRIPTION, genres=["realistic"])

    ctx = RefinementContext(
        original_description=DESCRIPTION,
        original_genres=["realistic"],
        iterations=[
            RefinementIteration(
                completions=round0,
                selected_index=0,
                instruction="Make it more exhausted and resigned.",
            )
        ],
    )

    agent = RefinementAgent()
    results = agent.run(ctx)

    assert isinstance(results, list)
    assert len(results) == 5
