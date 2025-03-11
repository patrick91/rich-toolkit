from typing import Any

from rich._loop import loop_first_last
from rich.console import Console, ConsoleOptions, Group, RenderableType, RenderResult
from rich.segment import Segment
from rich.text import Text

from rich_toolkit.element import CursorOffset, Element
from rich_toolkit.input import Input
from rich_toolkit.menu import Menu
from rich_toolkit.progress import Progress, ProgressLine

from .border import BorderedStyle


class FancyPanel:
    def __init__(
        self,
        renderable: RenderableType,
        title: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.renderable = renderable
        self._title = title
        self.style = "blue"
        self.border_style = "blue"
        self.metadata = metadata or {}
        self.width = None
        self.expand = True

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        renderable = self.renderable
        style = console.get_style(self.style)

        lines = console.render_lines(renderable, style=style)

        line_start = Segment("┌" if self.metadata.get("title") else "◆")
        new_line = Segment.line()

        if self._title is not None:
            yield line_start
            yield Segment(" ")
            yield self._title

        for first, last, line in loop_first_last(lines):
            if first and not self._title:
                decoration = "┌ " if self.metadata.get("title", False) else "◆ "
            elif last and self.metadata.get("started", True):
                decoration = "└ "
            else:
                decoration = "│ "

            yield Segment(decoration)
            yield from line

            if not last:
                yield new_line


class FancyStyle(BorderedStyle):
    theme = {
        "fancy.title": "bold cyan",
        "fancy.normal": "cyan",
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.cursor_offset = 2
        self.decoration_size = 2

    def decorate(
        self,
        renderable: Element | str,
        is_active: bool = False,
        **metadata: Any,
    ) -> RenderableType:
        title: str | None = None

        if isinstance(renderable, Element):
            rendered = renderable.render(is_active=is_active)
        else:
            rendered = renderable

        if isinstance(renderable, Progress):
            title = renderable.title

        if isinstance(renderable, ProgressLine):
            # TODO: call this decorate? or do decorate -> render
            return self.render_progress_log_line(
                rendered,
                index=metadata.get("index", 0),
                max_lines=metadata.get("max_lines", -1),
                total_lines=metadata.get("total_lines", -1),
            )

        content = FancyPanel(
            Group(
                rendered,
            ),
            title=title,
            metadata=metadata,
        )

        return content

    def empty_line(self) -> Text:
        """Return an empty line with decoration.

        Returns:
            A text object representing an empty line
        """
        return Text("│", style="fancy.normal")

    def get_cursor_offset_for_element(self, element: Element) -> CursorOffset:
        """Get the cursor offset for an element.

        Args:
            element: The element to get the cursor offset for

        Returns:
            The cursor offset
        """
        return CursorOffset(
            top=element.cursor_offset.top,
            left=self.decoration_size + element.cursor_offset.left,
        )
