from typing import Any, Callable, Optional

from rich.console import RenderableType
from rich.text import Text

from .element import Element


class Button(Element):
    def __init__(
        self,
        name: str,
        label: str,
        callback: Optional[Callable] = None,
        **metadata: Any,
    ):
        self.name = name
        self.label = label
        self.callback = callback

        super().__init__(**metadata)

    def render(self, is_active: bool = False) -> RenderableType:
        style = "black on blue" if is_active else "white on black"
        return Text(f" {self.label} ", style=style)

    def activate(self) -> Any:
        if self.callback:
            return self.callback()
        return True
