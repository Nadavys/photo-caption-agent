import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)

from agent_flow.agents.dialogue_completion_agent import DialogueCompletionAgent
from agent_flow.agents.refinement_agent import RefinementAgent
from agent_flow.refinement_context import RefinementContext, RefinementIteration

DESCRIPTION = "Woman standing in front of a bakery display case looking at a tray of fresh pastries, holding a wallet in her hand"
GENRES = ["humorous", "dramatic"]

# Round 0 — initial completions from DialogueCompletionAgent
print("=== Round 0 ===")
base_agent = DialogueCompletionAgent()
round0 = base_agent.run(DESCRIPTION, genres=GENRES)
for i, c in enumerate(round0, 1):
    print(f"{i}. {c}\n")

# Round 1 — pick completion 2 (index 1), ask to make it shorter
ctx = RefinementContext(
    original_description=DESCRIPTION,
    original_genres=GENRES,
    iterations=[
        RefinementIteration(
            completions=round0,
            selected_index=1,
            instruction="Make it shorter and more deadpan.",
        )
    ],
)

print("=== Round 1 (selected: 2, instruction: shorter + deadpan) ===")
refine_agent = RefinementAgent()
round1 = refine_agent.run(ctx)
for i, c in enumerate(round1, 1):
    print(f"{i}. {c}\n")

# Round 2 — pick completion 3 (index 2) from round 1, push it further
ctx.iterations.append(
    RefinementIteration(
        completions=round1,
        selected_index=2,
        instruction="Push the self-deprecating humor further.",
    )
)

print("=== Round 2 (selected: 3, instruction: more self-deprecating) ===")
round2 = refine_agent.run(ctx)
for i, c in enumerate(round2, 1):
    print(f"{i}. {c}\n")
