from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, NamedTuple

from rich.console import RenderableType


class CursorOffset(NamedTuple):
    top: int
    left: int


class Element(ABC):
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

    @abstractmethod
    def render(
        self,
        *,
        is_active: bool = False,
        done: bool = False,
        parent: Element | None = None,
    ) -> RenderableType:
        pass
