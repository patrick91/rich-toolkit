from typing import NamedTuple


class CursorOffset(NamedTuple):
    top: int
    left: int


class Element:
    cursor_offset: CursorOffset = CursorOffset(top=0, left=0)
    should_show_cursor: bool = False
