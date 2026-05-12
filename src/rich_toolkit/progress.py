from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from rich.console import Console, RenderableType
from rich.live import Live
from rich.text import Text

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
        self.lines_to_show = lines_to_show

        self.logs: List[ProgressLine] = []
        self._log_line_open = False

        self._cancelled = False

        Element.__init__(self, style=style, metadata=metadata)
        super().__init__(console=console, refresh_per_second=8, transient=transient)

    # TODO: remove this once rich uses "Self"
    def __enter__(self) -> "Progress":
        self.start(refresh=self._renderable is not None)

        return self

    def __exit__(self, exc_type: type | None, *args: object) -> None:
        if exc_type is KeyboardInterrupt:
            self._cancelled = True

        super().__exit__(exc_type, *args)

    def get_renderable(self) -> RenderableType:
        return self.style.render_element(self, done=not self._started)

    def _append_text(self, target: str | Text, text: str | Text) -> str | Text:
        if isinstance(target, str) and isinstance(text, str):
            return target + text

        return Text.assemble(target, text)

    def log(self, text: str | Text, end: str = "\n") -> None:
        should_append = self._log_line_open
        self._log_line_open = not end.endswith("\n")

        if end != "\n":
            text = self._append_text(text, end)

        if self._inline_logs:
            if should_append and self.logs:
                self.logs[-1].text = self._append_text(self.logs[-1].text, text)
            else:
                self.logs.append(ProgressLine(text, self))
        else:
            if should_append:
                self.current_message = self._append_text(self.current_message, text)
            else:
                self.current_message = text

    def set_error(self, text: str) -> None:
        self.current_message = text
        self.is_error = True
        self.transient = self._transient_on_error
        self._log_line_open = False
