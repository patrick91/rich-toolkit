from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from rich.console import Console, Group
from rich.live import Live, RenderableType
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

    def render(
        self,
        is_active: bool = False,
        done: bool = False,
        parent: Optional[Element] = None,
    ) -> RenderableType:
        content: str | Group | Text = self.current_message

        if self.logs and self._inline_logs:
            lines_to_show = (
                self.logs[-self.lines_to_show :]
                if self.lines_to_show > 0
                else self.logs
            )

            content = Group(
                *[
                    self.style.render_element(
                        line,
                        index=index,
                        max_lines=self.lines_to_show,
                        total_lines=len(self.logs),
                    )
                    for index, line in enumerate(lines_to_show)
                ]
            )

        return content

    def get_renderable(self) -> RenderableType:
        animation_status: Literal["started", "stopped", "error"] = (
            "started" if self._started else "stopped"
        )

        if self.is_error:
            animation_status = "error"

        if self.style is None:
            return self.render()

        return self.style.render(
            self,
            animation_status=animation_status,
            started=self._started,
        )

    def log(self, text: str | Text) -> None:
        if self._inline_logs:
            self.logs.append(ProgressLine(text, self))
        else:
            self.current_message = text

    def set_error(self, text: str) -> None:
        self.current_message = text
        self.is_error = True
        self.transient = self._transient_on_error
