from typing import Any

from rich.console import Console
from rich.segment import Segment

from .element import CursorOffset


class RenderWrapper:
    def __init__(self, content: Any, cursor_offset: CursorOffset) -> None:
        self.content = content
        self.cursor_offset = cursor_offset

    @property
    def size(self) -> tuple[int, int]:
        # TODO: use existing console
        console = Console()
        lines = console.render_lines(self.content, console.options, pad=False)

        shape = Segment.get_shape(lines)

        return shape
