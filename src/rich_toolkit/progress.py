from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from rich.console import Console, RenderableType
from rich.live import Live
from rich.text import Text
from typing_extensions import Literal

from .element import Element

if TYPE_CHECKING:
    from .styles.base import BaseStyle


class ProgressLine(Element):
    def __init__(self, text: str | Text, parent: Progress):
        self.text = text
        self.parent = parent


class Progress(Live, Element):
    current_message: str | Text

    def __init__(
        self,
        title: str,
        style: Optional[BaseStyle] = None,
        console: Optional[Console] = None,
        transient: bool = False,
        transient_on_error: bool = False,
        inline_logs: bool = False,
        lines_to_show: int = -1,
        **metadata: Dict[Any, Any],
    ) -> None:
        self.title = title
        self.current_message = title
        self.is_error = False
        self._transient_on_error = transient_on_error
        self._inline_logs = inline_logs
        self._style = style
        self.lines_to_show = lines_to_show

        self.logs: List[ProgressLine] = []

        super().__init__(console=console, refresh_per_second=8, transient=transient)
        self.metadata = metadata

        self._cancelled = False

    def get_renderable(self) -> RenderableType:
        return self.style.render_element(self)

    def log(self, text: str | Text) -> None:
        if self._inline_logs:
            self.logs.append(ProgressLine(text, self))
        else:
            self.current_message = text

        self.refresh()

    def set_error(self, text: str) -> None:
        self.current_message = text
        self.is_error = True
        self.transient = self._transient_on_error

        self.refresh()
