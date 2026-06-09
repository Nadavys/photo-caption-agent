from textual.app import App
from textual.binding import Binding

from agent_flow.refinement_context import RefinementContext


class CaptionApp(App):
    TITLE = "Caption Agent"
    BINDINGS = [Binding("q", "quit", "Quit", show=True)]

    description: str
    genres: list[str]
    image_path: str
    story_ideas: list[str]
    story_idea: str | None
    completions: list[str]
    selected_index: int
    refine_ctx: RefinementContext | None
    CSS = """
    Screen {
        overflow: hidden hidden;
    }

    VerticalScroll {
        height: 1fr;
        padding: 1 2;
    }

    .section-title {
        margin-top: 1;
        margin-bottom: 1;
        text-style: bold;
    }

    .selected-completion {
        border: solid $primary;
        padding: 1;
        margin-bottom: 1;
        background: $surface;
        height: auto;
    }

    .description-area {
        height: 6;
        max-height: 12;
    }

    TextArea.selected-completion {
        border: solid $primary;
        background: $surface;
        height: auto;
        max-height: 12;
        padding: 0 1;
    }

    .error {
        color: $error;
        margin-top: 1;
    }

    .status {
        color: $text-muted;
        margin-top: 1;
    }

    .actions {
        margin-top: 1;
        height: auto;
    }

    Button {
        margin-right: 1;
    }

    LoadingIndicator {
        height: 3;
        margin: 1 0;
    }

    ListView {
        margin-top: 1;
        border: solid $surface-lighten-1;
        max-height: 40;
    }

    ListItem {
        height: auto;
        padding: 1 2;
    }

    ListItem Label {
        width: 100%;
    }
    """

    def on_mount(self) -> None:
        self.description: str = ""
        self.genres: list[str] = []
        self.image_path: str = ""
        self.story_ideas: list[str] = []
        self.story_idea: str | None = None
        self.completions: list[str] = []
        self.selected_index: int = 0
        self.refine_ctx: RefinementContext | None = None
        from agent_flow.tui.screens.input import InputScreen
        self.push_screen(InputScreen())

    def start_over(self) -> None:
        self.description = ""
        self.genres = []
        self.image_path = ""
        self.story_ideas = []
        self.story_idea = None
        self.completions = []
        self.selected_index = 0
        self.refine_ctx = None
        from agent_flow.tui.screens.input import InputScreen
        self.switch_screen(InputScreen())
