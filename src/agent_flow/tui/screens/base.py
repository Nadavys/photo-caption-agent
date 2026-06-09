from textual.screen import Screen
from textual.widgets import Label


class BaseScreen(Screen):
    def _show_error(self, message: str) -> None:
        err = self.query_one("#error", Label)
        err.update(message)
        err.display = True
