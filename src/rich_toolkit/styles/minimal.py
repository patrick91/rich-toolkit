from typing import Any

from rich.console import RenderableType

from rich_toolkit.element import Element

from .base import BaseStyle


class MinimalStyle(BaseStyle):
    def decorate(
        self,
        renderable: Element | str,
        is_active: bool = False,
        done: bool = False,
        parent: Element | None = None,
        **metadata: Any,
    ) -> RenderableType:
        if isinstance(renderable, Element):
            return renderable.render(is_active=is_active, done=done, parent=parent)
        else:
            return renderable
