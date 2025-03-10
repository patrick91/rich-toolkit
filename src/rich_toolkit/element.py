from typing import Any, NamedTuple


class CursorOffset(NamedTuple):
    top: int
    left: int


class Element:
    metadata: dict = {}

    def __init__(self, **metadata: Any):
        self.metadata = metadata

        super().__init__()

    @property
    def cursor_offset(self) -> CursorOffset:
        return CursorOffset(top=0, left=0)

    @property
    def should_show_cursor(self) -> bool:
        return False
