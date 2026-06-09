import logging

from rich.markup import escape
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from agent_flow.tui.screens.base import BaseScreen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    ListItem,
    ListView,
    LoadingIndicator,
    Static,
)

from agent_flow.agents.dialogue_completion_agent import DialogueCompletionAgent
from agent_flow.agents.story_idea_agent import StoryIdeaAgent

log = logging.getLogger(__name__)


class StoryIdeasScreen(BaseScreen):
    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll():
            yield Static("Choose a story direction:", classes="section-title")
            with ListView(id="ideas"):
                for i, idea in enumerate(self.app.story_ideas):
                    yield ListItem(Label(f"[bold]{i + 1}.[/bold]  {escape(idea)}"))
            with Horizontal(classes="actions"):
                yield Button("Select", id="select", variant="primary")
                yield Button("10 More", id="more")
                yield Button("Skip", id="skip")
            yield LoadingIndicator(id="loading")
            yield Label("", id="status", classes="status")
            yield Label("", id="error", classes="error")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#loading").display = False
        self.query_one("#status").display = False
        self.query_one("#error").display = False

    @on(Button.Pressed, "#select")
    def on_select(self) -> None:
        lv = self.query_one("#ideas", ListView)
        idx = lv.index
        if idx is None:
            self._show_error("Select a story direction first.")
            return
        self.query_one("#error").display = False
        chosen = self.app.story_ideas[idx]
        self.app.story_idea = chosen
        self._set_loading(True, "Generating completions…")
        self._run_dialogue(chosen)

    @on(Button.Pressed, "#more")
    def on_more(self) -> None:
        self.query_one("#error").display = False
        self._set_loading(True, "Generating 10 more ideas…")
        self._run_more_ideas(list(self.app.story_ideas))

    @on(Button.Pressed, "#skip")
    def on_skip(self) -> None:
        self.app.story_idea = None
        self._set_loading(True, "Generating completions…")
        self._run_dialogue(None)

    @work(thread=True)
    def _run_more_ideas(self, exclude: list[str]) -> None:
        try:
            agent = StoryIdeaAgent()
            ideas = agent.run(self.app.description, self.app.genres, exclude=exclude)
            self.app.call_from_thread(self._on_more_success, ideas)
        except Exception as exc:
            log.exception("[story-ideas] idea agent error")
            self.app.call_from_thread(self._on_error, str(exc))

    def _on_more_success(self, ideas: list[str]) -> None:
        self.app.story_ideas = ideas
        self._set_loading(False)
        lv = self.query_one("#ideas", ListView)
        lv.clear()
        for i, idea in enumerate(ideas):
            lv.append(ListItem(Label(f"[bold]{i + 1}.[/bold]  {escape(idea)}")))

    @work(thread=True)
    def _run_dialogue(self, story_idea: str | None) -> None:
        try:
            agent = DialogueCompletionAgent()
            completions = agent.run(
                self.app.description,
                self.app.genres,
                story_idea=story_idea,
            )
            self.app.call_from_thread(self._on_dialogue_success, completions)
        except Exception as exc:
            log.exception("[story-ideas] dialogue agent error")
            self.app.call_from_thread(self._on_error, str(exc))

    def _on_dialogue_success(self, completions: list[str]) -> None:
        self.app.completions = completions
        from agent_flow.tui.screens.results import ResultsScreen
        self._set_loading(False)
        self.app.switch_screen(ResultsScreen())

    def _on_error(self, message: str) -> None:
        self._set_loading(False)
        self._show_error(f"Error: {escape(message)}")

    def _set_loading(self, active: bool, status: str = "") -> None:
        self.query_one("#loading").display = active
        status_label = self.query_one("#status", Label)
        status_label.update(status)
        status_label.display = active
        self.query_one("#select", Button).disabled = active
        self.query_one("#more", Button).disabled = active
        self.query_one("#skip", Button).disabled = active
        if active:
            self.query_one("#error").display = False

