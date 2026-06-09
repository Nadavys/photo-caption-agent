from rich.markup import escape
from textual.widgets import Static

from agent_flow.refinement_context import RefinementContext


class ContextPanel(Static):
    """Persistent summary bar shown on every post-input screen."""

    DEFAULT_CSS = """
    ContextPanel {
        border: solid $surface-lighten-2;
        background: $panel;
        padding: 1;
        margin-bottom: 1;
        height: auto;
    }
    """

    def __init__(
        self,
        description: str,
        genres: list[str],
        refine_ctx: RefinementContext | None = None,
        image_filename: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(self._build(description, genres, refine_ctx, image_filename), **kwargs)

    @staticmethod
    def _build(
        description: str,
        genres: list[str],
        refine_ctx: RefinementContext | None,
        image_filename: str | None,
    ) -> str:
        if image_filename:
            parts = [f"[bold]Image:[/bold] {escape(image_filename)}"]
        else:
            parts = [f"[bold]Description:[/bold] {escape(description)}"]
        if genres:
            parts.append(f"[bold]Genres:[/bold] {escape(', '.join(genres))}")

        if refine_ctx and refine_ctx.iterations:
            parts.append("")
            parts.append("[bold]Refinement history:[/bold]")
            for i, it in enumerate(refine_ctx.iterations, 1):
                selected = it.completions[it.selected_index] if it.selected_index < len(it.completions) else ""
                preview = escape(selected[:80] + ("…" if len(selected) > 80 else ""))
                parts.append(f'  [dim]Round {i}:[/dim] "{preview}"')
                parts.append(f"  [dim]→[/dim] {escape(it.instruction)}")

        return "\n".join(parts)
