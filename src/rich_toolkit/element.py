from typing import NamedTuple


class CursorOffset(NamedTuple):
    top: int
    left: int


class Element:
    @property
    def cursor_offset(self) -> CursorOffset:
        return CursorOffset(top=0, left=0)

    @property
    def should_show_cursor(self) -> bool:
        return False
