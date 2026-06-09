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
    Input,
    Label,
    LoadingIndicator,
    SelectionList,
    Static,
    TextArea,
)

from agent_flow.agents.story_idea_agent import StoryIdeaAgent
from agent_flow.genres import GENRES

log = logging.getLogger(__name__)


class InputScreen(BaseScreen):
    def __init__(self) -> None:
        super().__init__()
        self._analyzed_image_path: str | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll():
            yield Static("Image path (optional)", classes="section-title")
            yield Input(placeholder="e.g. /Users/me/photos/portrait.jpg", id="image-path")
            yield Static("Photo description", classes="section-title")
            yield TextArea(id="description", classes="description-area")
            yield Static("Genres (optional)", classes="section-title")
            yield SelectionList(*[(key.capitalize(), key) for key in GENRES], id="genres")
            with Horizontal(classes="actions"):
                yield Button("Generate", id="generate", variant="primary")
                yield Button("Confirm description →", id="confirm", variant="primary")
            yield LoadingIndicator(id="loading")
            yield Label("", id="status", classes="status")
            yield Label("", id="error", classes="error")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#loading").display = False
        self.query_one("#status").display = False
        self.query_one("#error").display = False
        self.query_one("#confirm").display = False

    @on(Input.Changed, "#image-path")
    def on_image_path_changed(self, event: Input.Changed) -> None:
        has_image = bool(event.value.strip())
        desc = self.query_one("#description", TextArea)
        desc.disabled = has_image
        if has_image:
            desc.load_text("")
        # If user edits the image path after vision analysis, reset to generate mode
        if self._analyzed_image_path is not None:
            self._reset_to_generate_mode()

    @on(Input.Submitted, "#image-path")
    def on_image_path_submitted(self) -> None:
        self.on_generate()

    @on(Button.Pressed, "#generate")
    def on_generate(self) -> None:
        image_path = self.query_one("#image-path", Input).value.strip()
        desc = self.query_one("#description", TextArea).text.strip()
        if not image_path and not desc:
            self._show_error("Please enter a photo description or provide an image path.")
            return
        genres = list(self.query_one("#genres", SelectionList).selected)
        self._set_loading(True, "Analyzing image…" if image_path else "Generating story ideas…")
        if image_path:
            self._run_vision(image_path, genres)
        else:
            self._run_story_ideas(desc, genres, None)

    @on(Button.Pressed, "#confirm")
    def on_confirm(self) -> None:
        description = self.query_one("#description", TextArea).text.strip()
        if not description:
            self._show_error("Description is empty.")
            return
        genres = list(self.query_one("#genres", SelectionList).selected)
        self._set_loading(True, "Generating story ideas…")
        self._run_story_ideas(description, genres, self._analyzed_image_path)

    @work(thread=True)
    def _run_vision(self, image_path: str, genres: list[str]) -> None:
        try:
            from agent_flow.agents.vision_agent import VisionAgent
            description = VisionAgent().describe(image_path)
            self.app.call_from_thread(self._on_vision_done, description, image_path, genres)
        except Exception as exc:
            log.exception("[input] vision agent error")
            self.app.call_from_thread(self._on_error, str(exc))

    def _on_vision_done(self, description: str, image_path: str, genres: list[str]) -> None:
        current_path = self.query_one("#image-path", Input).value.strip()
        if current_path != image_path:
            self._set_loading(False)
            return
        self._analyzed_image_path = image_path
        self._set_loading(False)
        desc_input = self.query_one("#description", TextArea)
        desc_input.load_text(description)
        desc_input.disabled = False
        self.query_one("#generate").display = False
        self.query_one("#confirm").display = True
        self.query_one("#status", Label).update("Description generated from image — edit if needed, then confirm.")
        self.query_one("#status").display = True

    @work(thread=True)
    def _run_story_ideas(self, description: str, genres: list[str], image_path: str | None) -> None:
        try:
            agent = StoryIdeaAgent()
            ideas = agent.run(description, genres)
            self.app.call_from_thread(self._on_success, description, genres, image_path or "", ideas)
        except Exception as exc:
            log.exception("[input] agent error")
            self.app.call_from_thread(self._on_error, str(exc))

    def _on_success(self, description: str, genres: list[str], image_path: str, ideas: list[str]) -> None:
        self.app.description = description
        self.app.genres = genres
        self.app.image_path = image_path
        self.app.story_ideas = ideas
        from agent_flow.tui.screens.story_ideas import StoryIdeasScreen
        self._set_loading(False)
        self.query_one("#error").display = False
        self.app.switch_screen(StoryIdeasScreen())

    def _on_error(self, message: str) -> None:
        if self._analyzed_image_path is None:
            self._reset_to_generate_mode()
        self._set_loading(False)
        self._show_error(f"Error: {escape(message)}")

    def _reset_to_generate_mode(self) -> None:
        self._analyzed_image_path = None
        self.query_one("#generate").display = True
        self.query_one("#confirm").display = False
        self.query_one("#status").display = False

    def _set_loading(self, active: bool, status: str = "") -> None:
        self.query_one("#loading").display = active
        status_label = self.query_one("#status", Label)
        if status:
            status_label.update(status)
        status_label.display = active
        in_confirm_mode = self._analyzed_image_path is not None
        if in_confirm_mode:
            self.query_one("#confirm", Button).disabled = active
        else:
            self.query_one("#generate", Button).disabled = active
        self.query_one("#image-path", Input).disabled = active
        if active:
            self.query_one("#description", TextArea).disabled = True
            self.query_one("#error").display = False
        else:
            if not in_confirm_mode:
                has_image = bool(self.query_one("#image-path", Input).value.strip())
                self.query_one("#description", TextArea).disabled = has_image

