import logging
from pathlib import Path

from rich.markup import escape
from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from agent_flow.tui.screens.base import BaseScreen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    LoadingIndicator,
    TextArea,
)

from agent_flow.agents.refinement_agent import RefinementAgent
from agent_flow.refinement_context import RefinementContext, RefinementIteration
from agent_flow.tui.widgets import ContextPanel

log = logging.getLogger(__name__)


class RefineScreen(BaseScreen):
    BINDINGS = [Binding("c", "copy_completion", "Copy", show=True)]

    def compose(self) -> ComposeResult:
        idx = self.app.selected_index
        completions = self.app.completions
        selected = completions[idx] if completions and 0 <= idx < len(completions) else ""
        yield Header()
        with VerticalScroll():
            yield ContextPanel(
                self.app.description,
                self.app.genres,
                self.app.refine_ctx,
                image_filename=Path(self.app.image_path).name if self.app.image_path else None,
            )
            yield Label("Selected completion (select text to copy, or press C for full copy):", classes="section-title")
            yield TextArea(selected, read_only=True, show_line_numbers=False, id="selected-text", classes="selected-completion")
            yield Label("Refinement instruction", classes="section-title")
            yield Input(placeholder="e.g. Make it shorter and more deadpan.", id="instruction")
            with Horizontal(classes="actions"):
                yield Button("Refine", id="refine", variant="primary")
                yield Button("Start Over", id="start-over")
            yield LoadingIndicator(id="loading")
            yield Label("Refining…", id="status", classes="status")
            yield Label("", id="error", classes="error")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#loading").display = False
        self.query_one("#status").display = False
        self.query_one("#error").display = False

    def action_copy_completion(self) -> None:
        idx = self.app.selected_index
        completions = self.app.completions
        if not completions or not (0 <= idx < len(completions)):
            return
        self.app.copy_to_clipboard(completions[idx])
        self.notify("Copied!", timeout=2)

    @on(Input.Submitted, "#instruction")
    def on_instruction_submitted(self) -> None:
        self.on_refine()

    @on(Button.Pressed, "#refine")
    def on_refine(self) -> None:
        instruction = self.query_one("#instruction", Input).value.strip()
        if not instruction:
            self._show_error("Please enter a refinement instruction.")
            return
        if self.app.refine_ctx is None:
            self.app.refine_ctx = RefinementContext(
                original_description=self.app.description,
                original_genres=self.app.genres,
                story_idea=self.app.story_idea,
            )
        self.app.refine_ctx.iterations.append(
            RefinementIteration(
                completions=self.app.completions,
                selected_index=self.app.selected_index,
                instruction=instruction,
            )
        )
        self._set_loading(True)
        self._run_refine(self.app.refine_ctx)

    @work(thread=True)
    def _run_refine(self, ctx: RefinementContext) -> None:
        try:
            agent = RefinementAgent()
            completions = agent.run(ctx)
            self.app.call_from_thread(self._on_success, completions)
        except Exception as exc:
            log.exception("[refine] agent error")
            self.app.call_from_thread(self._on_error, str(exc))

    def _on_success(self, completions: list[str]) -> None:
        self.app.completions = completions
        from agent_flow.tui.screens.refined import RefinedResultsScreen
        self._set_loading(False)
        self.app.switch_screen(RefinedResultsScreen())

    def _on_error(self, message: str) -> None:
        self._set_loading(False)
        if self.app.refine_ctx and self.app.refine_ctx.iterations:
            self.app.refine_ctx.iterations.pop()
        self._show_error(f"Error: {escape(message)}")

    def _set_loading(self, active: bool) -> None:
        self.query_one("#loading").display = active
        self.query_one("#status").display = active
        self.query_one("#refine", Button).disabled = active
        self.query_one("#start-over", Button).disabled = active
        self.query_one("#instruction", Input).disabled = active
        if active:
            self.query_one("#error").display = False

