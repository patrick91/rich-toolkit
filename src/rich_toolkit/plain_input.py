# this will become the input class, but for now we make a copy
# so we don't fear to change stuff
from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple

import click
from rich.console import Console, Group, RenderableType
from rich.control import Control
from rich.live_render import LiveRender

from rich_toolkit.styles.base import BaseStyle

from .input import TextInputHandler


class Input(TextInputHandler):
    def __init__(
        self,
        console: Console,
        style: Optional[BaseStyle] = None,
        default: str = "",
        container: ... = None,
        cursor_offset: int = 0,
        # TODO: call this is_secure?
        password: bool = False,
        **metadata: Any,
    ):
        self.default = default
        self.password = password
        self.container = container

        self.console = console
        self.style = style
        self.text = ""
        self.valid: bool | None = None

        super().__init__(cursor_offset=cursor_offset)

    @property
    def should_show_cursor(self) -> bool:
        return True

    def on_blur(self):
        self.valid = bool(self.text)

    def render_input(self) -> RenderableType:
        text = self.text

        if self.password:
            text = "*" * len(self.text)

        # if there's no default value, add a space to keep the cursor visible
        # and, most importantly, in the right place
        default = self.default or " "

        text = f"[text]{text}[/]" if self.text else f"[placeholder]{default}[/]"

        return text

    def render_result(self) -> RenderableType:
        return self.render_input()

    def render(self, is_active: bool = False) -> RenderableType:
        return self.render_input()

    def handle_key(self, key: str) -> None:
        if key == "\r":
            print("enter")
