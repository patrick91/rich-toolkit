from __future__ import annotations


from typing import Any, NamedTuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .styles import BaseStyle


class CursorOffset(NamedTuple):
    top: int
    left: int


class Element:
    metadata: dict = {}

    def __init__(self, **metadata: Any):
        self.metadata = metadata

        self._cancelled = False
        self._style: Union[BaseStyle, None] = None

        super().__init__()

    @property
    def cursor_offset(self) -> CursorOffset:
        return CursorOffset(top=0, left=0)

    @property
    def should_show_cursor(self) -> bool:
        return False

    @property
    def style(self) -> BaseStyle:
        from .styles import MinimalStyle

        return self._style or MinimalStyle()

    def handle_key(self, key: str) -> None:  # noqa: B027
        pass

    def on_cancel(self) -> None:  # noqa: B027
        self._cancelled = True
