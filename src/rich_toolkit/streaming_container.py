from typing import Tuple

from rich.console import (
    Group,
    RenderableType,
)
from rich.live import Live

from .container import Container
from .element import Element


class StreamingContainer(Live, Element):
    def __init__(self, container: "Container"):
        self.container = container
        self.container.title = "Streaming container"
        self.logs = []
        self.footer_content = ""
        super().__init__()

    def log(self, text: str):
        self.logs.append(text)

    def footer(self, text: str):
        self.footer_content = text

    def __enter__(self):
        self.start()

        return self

    def render(self, is_active: bool = False) -> RenderableType:
        return Group(
            *self.logs,
            self.footer_content,
        )

    def get_renderable(self) -> RenderableType:
        return self.container.style.decorate(self).content
