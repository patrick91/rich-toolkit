from typing import Any, Union, Optional

from rich.console import RenderableType

from rich_toolkit.element import Element

from .base import BaseStyle


class MinimalStyle(BaseStyle):
    def render(
        self,
        renderable: Union[Element, str],
        is_active: bool = False,
        done: bool = False,
        parent: Optional[Element] = None,
        **metadata: Any,
    ) -> RenderableType:
        if isinstance(renderable, Element):
            return renderable.render(is_active=is_active, done=done, parent=parent)
        else:
            return renderable
