from typing import Optional

from rich.console import RenderableType

from .base import BaseStyle


class MinimalStyle(BaseStyle):
    def render_context_enter(self) -> Optional[RenderableType]:
        return None

    def render_context_exit(self) -> Optional[RenderableType]:
        return None
