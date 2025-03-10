from typing import Any, Generator, Iterable, List

from rich._loop import loop_first_last
from rich.box import Box
from rich.console import Group, RenderableType
from rich.padding import Padding
from rich.segment import Segment
from rich.style import Style
from rich.text import Text

from rich_toolkit.element import CursorOffset, Element
from rich_toolkit.input import Input
from rich_toolkit.menu import Menu
from rich_toolkit.panel import Panel
from rich_toolkit.progress import Progress, ProgressLine

from .border import BorderedStyle


class FancyPanel:
    def __init__(
        self, renderable: RenderableType, title: str, metadata: dict[str, Any]
    ) -> None:
        self.renderable = renderable
        self._title = title
        self.style = "blue"
        self.border_style = "blue"
        self.metadata = metadata
        self.width = None
        self.expand = True
        self.padding = (0, 0)

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        # copied from Panel.__rich_console__
        _padding = Padding.unpack(self.padding)
        renderable = (
            Padding(self.renderable, _padding) if any(_padding) else self.renderable
        )
        style = console.get_style(self.style)

        lines = console.render_lines(renderable, style=style)

        line_start = Segment("┌" if self.metadata.get("title") else "◆")
        line_start_last = Segment("└")
        new_line = Segment.line()

        if self._title is not None:
            yield line_start
            yield Segment(" ")
            yield self._title
            # yield new_line

        for first, last, line in loop_first_last(lines):
            if first and not self._title:
                decoration = "┌ " if self.metadata.get("title", False) else "◆ "
            elif last:
                decoration = "└ "
            else:
                decoration = "│ "

            yield Segment(decoration)
            yield from line

            if not last:
                yield new_line

            yield line_start_last


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
        validation_message: tuple[str, ...] = ()

        if isinstance(renderable, Input):
            if renderable.valid is False:
                validation_message = (Text("This field is required", style="bold red"),)
            else:
                validation_message = ()

            renderable._should_show_label = False
            renderable._should_show_validation = False

            title = renderable.render_label(is_active=is_active)

        if isinstance(renderable, Menu):
            title = renderable.render_label()

            renderable._should_show_label = False
            renderable._should_show_validation = False

        if isinstance(renderable, Progress):
            title = renderable.title

        if isinstance(renderable, Element):
            rendered = renderable.render(is_active=is_active)
        else:
            rendered = renderable

        if isinstance(renderable, ProgressLine):
            # TODO: call this decorate? or do decorate -> render
            return self.render_progress_log_line(
                rendered,
                index=metadata.get("index", 0),
                max_lines=metadata.get("max_lines", -1),
                total_lines=metadata.get("total_lines", -1),
            )

        content = Group(
            FancyPanel(
                rendered,
                title=title,
                metadata=metadata,
            ),
            *validation_message,
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
