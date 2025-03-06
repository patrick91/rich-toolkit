from typing import Any

from rich.console import Console
from rich.segment import Segment

from .element import CursorOffset


class RenderWrapper:
    def __init__(self, content: Any, cursor_offset: CursorOffset) -> None:
        self.content = content
        self.cursor_offset = cursor_offset

