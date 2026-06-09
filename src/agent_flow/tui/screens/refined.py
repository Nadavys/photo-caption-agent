from pathlib import Path

from rich.markup import escape
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from agent_flow.tui.screens.base import BaseScreen
from textual.widgets import Button, Footer, Header, Label, ListItem, ListView, Static

from agent_flow.tui.widgets import ContextPanel


class RefinedResultsScreen(BaseScreen):
    BINDINGS = [Binding("c", "copy_completion", "Copy", show=True)]

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll():
            yield ContextPanel(
                self.app.description,
                self.app.genres,
                self.app.refine_ctx,
                image_filename=Path(self.app.image_path).name if self.app.image_path else None,
            )
            yield Static("Select a refined completion:", classes="section-title")
            with ListView(id="completions"):
                for i, text in enumerate(self.app.completions):
                    yield ListItem(Label(f"[bold]{i + 1}.[/bold]  {escape(text)}"))
            with Horizontal(classes="actions"):
                yield Button("Refine Again", id="refine-again", variant="primary")
                yield Button("Start Over", id="start-over")
            yield Label("", id="error", classes="error")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#error").display = False

    @on(Button.Pressed, "#refine-again")
    def on_refine_again(self) -> None:
        lv = self.query_one("#completions", ListView)
        idx = lv.index
        if idx is None:
            self._show_error("Select a completion first.")
            return
        self.query_one("#error").display = False
        self.app.selected_index = idx
        from agent_flow.tui.screens.refine import RefineScreen
        self.app.switch_screen(RefineScreen())

    @on(Button.Pressed, "#start-over")
    def on_start_over(self) -> None:
        self.app.start_over()

    def action_copy_completion(self) -> None:
        lv = self.query_one("#completions", ListView)
        idx = lv.index
        if idx is None or idx >= len(self.app.completions):
            return
        self.app.copy_to_clipboard(self.app.completions[idx])
        self.notify("Copied!", timeout=2)

