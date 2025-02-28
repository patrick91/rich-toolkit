# this will become the input class, but for now we make a copy
# so we don't fear to change stuff
from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple

import click
from rich.console import Console, Group, RenderableType
from rich.control import Control
from rich.live_render import LiveRender

from rich_toolkit.styles.base import BaseStyle

from .input import LiveInput


class Input(LiveInput):
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

        super().__init__(
            console=console,
            style=style,
            cursor_offset=cursor_offset,
            **metadata,
        )

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

    def ask(self) -> str:
        self._refresh()

        while True:
            try:
                key = click.getchar()

                if key == "\r":
                    break

                self.update_text(key)
                if self.container:
                    self.container.on_update(self)

            except KeyboardInterrupt:
                exit()

            self._refresh()

        self._refresh(show_result=True)

        for _ in range(self._padding_bottom):
            self.console.print()

        return self.text or self.default
