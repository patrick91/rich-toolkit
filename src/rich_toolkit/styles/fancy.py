from typing import Any, Union, Optional

from rich._loop import loop_first_last
from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.segment import Segment
from rich.text import Text
from rich.style import Style
from typing import Dict
from rich_toolkit.element import CursorOffset, Element
from rich_toolkit.progress import Progress, ProgressLine
from rich_toolkit.styles.base import BaseStyle

from .border import BorderedStyle


class FancyPanel:
    def __init__(
        self,
        renderable: RenderableType,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_animated: Optional[bool] = None,
        animation_counter: Optional[int] = None,
        style: Optional[BaseStyle] = None,
    ) -> None:
        self.renderable = renderable
        self._title = title
        self.metadata = metadata or {}
        self.width = None
        self.expand = True
        self.is_animated = is_animated
        self.counter = animation_counter or 0
        self.style = style

    def _get_decoration(self, suffix: str = "") -> Segment:
        char = "┌" if self.metadata.get("title") else "◆"

        if self.is_animated and self.style is not None:
            color = self.style._get_animation_colors(
                steps=14, breathe=True, animation_status="started"
            )[self.counter % 14]

            return Segment(char + suffix, style=Style.from_color(color))
        else:
            return Segment(char + suffix, style=Style(color="green"))

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        renderable = self.renderable

        lines = console.render_lines(renderable)

        line_start = self._get_decoration()

        new_line = Segment.line()

        if self._title is not None:
            yield line_start
            yield Segment(" ")
            yield self._title

        for first, last, line in loop_first_last(lines):
            if first and not self._title:
                decoration = (
                    Segment("┌ ")
                    if self.metadata.get("title", False)
                    else self._get_decoration(suffix=" ")
                )
            elif last and self.metadata.get("started", True):
                decoration = Segment("└ ")
            else:
                decoration = Segment("│ ")

            yield decoration
            yield from line

            if not last:
                yield new_line


class FancyStyle(BorderedStyle):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.cursor_offset = 2
        self.decoration_size = 2

    def render(
        self,
        renderable: Union[Element, str],
        is_active: bool = False,
        done: bool = False,
        parent: Optional[Element] = None,
        **metadata: Any,
    ) -> RenderableType:
        title: Optional[str] = None
        is_animated: Optional[bool] = None

        if isinstance(renderable, Element):
            rendered = renderable.render(is_active=is_active, done=done, parent=parent)
        else:
            rendered = renderable

        if isinstance(renderable, Progress):
            title = renderable.title
            is_animated = True

        if isinstance(renderable, ProgressLine):
            return self.render_progress_log_line(
                rendered,
                index=metadata.get("index", 0),
                max_lines=metadata.get("max_lines", -1),
                total_lines=metadata.get("total_lines", -1),
            )

        content = FancyPanel(
            rendered,
            title=title,
            metadata=metadata,
            is_animated=is_animated,
            animation_counter=self.animation_counter,
            style=self,
        )

        # TODO: maybe this should be based on the renderable?
        self.animation_counter += 1

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
