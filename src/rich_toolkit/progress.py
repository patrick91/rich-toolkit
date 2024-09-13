from typing import Optional

from rich.console import Console
from rich.live import Live
from typing_extensions import Any, Literal

from .styles.base import BaseStyle


class Progress(Live):
    def __init__(
        self,
        title: str,
        style: Optional[BaseStyle] = None,
        console: Optional[Console] = None,
        transient: bool = False,
        transient_on_error: bool = False,
    ) -> None:
        self.current_message = title
        self.style = style
        self.is_error = False
        self._transient_on_error = transient_on_error

        super().__init__(console=console, refresh_per_second=8, transient=transient)

    # TODO: remove this once rich uses "Self"
    def __enter__(self) -> "Progress":
        self.start(refresh=self._renderable is not None)

        return self

    def get_renderable(self) -> Any:
        current_message = self.current_message

        if not self.style:
            return current_message

        animation_status: Literal["started", "stopped", "error"] = (
            "started" if self._started else "stopped"
        )

        if self.is_error:
            animation_status = "error"

        return self.style.with_decoration(
            current_message,
            animation_status=animation_status,
        )

    def log(self, text: str) -> None:
        self.current_message = text

    def set_error(self, text: str) -> None:
        self.current_message = text
        self.is_error = True
        self.transient = self._transient_on_error
