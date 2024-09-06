from typing import Optional

from rich.color import Color
from rich.console import Console
from rich.live import Live
from typing_extensions import Any

from .styles.base import BaseStyle


class Progress(Live):
    def __init__(
        self,
        title: str,
        style: Optional[BaseStyle] = None,
        console: Optional[Console] = None,
        transient: bool = False,
    ) -> None:
        self.current_message = title
        self.style = style
        self.is_error = False

        super().__init__(console=console, refresh_per_second=8, transient=transient)

    # TODO: remove this once rich uses "Self"
    def __enter__(self) -> "Progress":
        self.start(refresh=self._renderable is not None)

        return self

    def get_renderable(self) -> Any:
        current_message = self.current_message

        if not self.style:
            return current_message

        return self.style.with_decoration(
            current_message, animated=True, is_error=self.is_error
        )

    def log(self, text: str) -> None:
        self.current_message = text

    def set_error(self, text: str) -> None:
        self.current_message = text
        self.is_error = True
