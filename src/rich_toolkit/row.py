from typing import Any

from rich.console import Console, ConsoleOptions, RenderableType, RenderResult

from .app_style import AppStyle


class RowWithDecoration:
    def __init__(
        self,
        content: RenderableType,
        style: AppStyle,
        animated: bool = False,
        **metadata: Any,
    ) -> None:
        self.content = content
        self.style = style
        self.metadata = metadata
        self.animated = animated

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        lines = console.render_lines(self.content, options, pad=False)

        # )

        yield from self.style.decorate(lines, animated=self.animated, **self.metadata)
