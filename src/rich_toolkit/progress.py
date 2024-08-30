from typing import Optional

from rich.color import Color
from rich.console import Console
from rich.live import Live
from typing_extensions import Any

from .app_style import AppStyle


class Progress(Live):
    def __init__(
        self,
        title: str,
        style: AppStyle,
        console: Optional[Console] = None,
    ) -> None:
        self.current_message = title
        self.style = style

        super().__init__(console=console, refresh_per_second=8)

    # TODO: remove this once rich uses "Self"
    def __enter__(self) -> "Progress":
        self.start(refresh=self._renderable is not None)
        return self

    def get_renderable(self) -> Any:
        return self.style.with_decoration(self.current_message, animated=True)

    def log(self, text: str) -> None:
        self.current_message = text

    def set_error(self, text: str) -> None:
        self.current_message = text
        self.colors = [Color.parse("red")]
