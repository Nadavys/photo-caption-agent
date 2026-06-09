from dataclasses import dataclass, field


@dataclass
class RefinementIteration:
    completions: list[str]
    selected_index: int
    instruction: str


@dataclass
class RefinementContext:
    original_description: str
    original_genres: list[str] | None
    story_idea: str | None = None
    iterations: list[RefinementIteration] = field(default_factory=list)
