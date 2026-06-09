import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)

from agent_flow.agents.dialogue_completion_agent import DialogueCompletionAgent
from agent_flow.agents.story_idea_agent import StoryIdeaAgent

DESCRIPTION = "Woman standing in front of a bakery display case looking at a tray of fresh pastries, holding a wallet in her hand"
GENRES = ["humorous", "dramatic"]

# Step 1: generate story ideas
print("\n=== Story Ideas (10) ===")
idea_agent = StoryIdeaAgent()
ideas = idea_agent.run(DESCRIPTION, genres=GENRES)
for i, idea in enumerate(ideas, 1):
    print(f"{i}. {idea}")

# Step 2: pick the first idea (in the TUI the user selects interactively)
chosen = ideas[0]
print(f"\n>>> Selected: {chosen}\n")

# Step 3: generate dialogue completions grounded in the chosen idea
print("=== Dialogue Completions ===")
dialogue_agent = DialogueCompletionAgent()
completions = dialogue_agent.run(DESCRIPTION, genres=GENRES, story_idea=chosen)
for i, line in enumerate(completions, 1):
    print(f"\n{i}. {line}")
