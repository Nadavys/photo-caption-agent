"""
Integration test: story-idea → dialogue → refinement (full new flow).

Exercises:
  1. StoryIdeaAgent generates 10 story ideas from a description + genre.
  2. User picks idea[0] — passed to DialogueCompletionAgent as story_idea.
  3. DialogueCompletionAgent generates 4 dialogue completions grounded in the chosen idea.
  4. User picks completion[0] with an instruction — passed to RefinementAgent.
  5. RefinementAgent returns 5 refined completions carrying the story context.
"""
import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("OLLAMA_API_KEY"),
    reason="OLLAMA_API_KEY not set",
)

DESCRIPTION = "Woman sitting at a café table staring at a laptop with an empty coffee cup beside her."
GENRES = ["realistic"]


def test_full_flow_story_idea_to_refinement():
    from agent_flow.agents.dialogue_completion_agent import DialogueCompletionAgent
    from agent_flow.agents.refinement_agent import RefinementAgent
    from agent_flow.agents.story_idea_agent import StoryIdeaAgent
    from agent_flow.refinement_context import RefinementContext, RefinementIteration

    # Step 1: generate story ideas
    idea_agent = StoryIdeaAgent()
    ideas = idea_agent.run(DESCRIPTION, genres=GENRES)

    assert isinstance(ideas, list), "ideas should be a list"
    assert len(ideas) == 10, f"expected 10 ideas, got {len(ideas)}"
    assert all(isinstance(i, str) and i for i in ideas), "each idea should be a non-empty string"

    # Step 2: user picks idea[0]; generate dialogue grounded in that idea
    chosen_idea = ideas[0]
    dialogue_agent = DialogueCompletionAgent()
    completions = dialogue_agent.run(DESCRIPTION, genres=GENRES, story_idea=chosen_idea)

    assert isinstance(completions, list), "completions should be a list"
    assert len(completions) == 4, f"expected 4 completions, got {len(completions)}"
    assert all(isinstance(c, str) and c for c in completions), "each completion should be a non-empty string"

    # Step 3: user picks completion[0] and requests a refinement
    ctx = RefinementContext(
        original_description=DESCRIPTION,
        original_genres=GENRES,
        story_idea=chosen_idea,
        iterations=[
            RefinementIteration(
                completions=completions,
                selected_index=0,
                instruction="Make it more exhausted and resigned.",
            )
        ],
    )

    refine_agent = RefinementAgent()
    refined = refine_agent.run(ctx)

    assert isinstance(refined, list), "refined should be a list"
    assert len(refined) == 5, f"expected 5 refined completions, got {len(refined)}"
    assert all(isinstance(r, str) and r for r in refined), "each refined completion should be a non-empty string"
