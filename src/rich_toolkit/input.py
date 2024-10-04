import string
from typing import Any, Optional

import click
from rich.console import Console, Group, RenderableType
from rich.control import Control
from rich.live_render import LiveRender

from rich_toolkit.styles.base import BaseStyle


class Input:
    def __init__(
        self,
        console: Console,
        title: str,
        style: Optional[BaseStyle] = None,
        default: str = "",
        cursor_offset: int = 0,
        password: bool = False,
        **metadata: Any,
    ):
        self.title = title
        self.default = default
        self.text = ""
        self._cursor_offset = cursor_offset
        self.password = password

        self.console = console
        self.style = style

        if style is None:
            self._live_render = LiveRender("")
        else:
            self._live_render = style.decorate_class(LiveRender, **metadata)("")

        self._padding_bottom = 1

    def _update_text(self, char: str) -> None:
        if char == "\x7f":
            self.text = self.text[:-1]
        elif char in string.printable:
            self.text += char

    def _render_result(self) -> RenderableType:
        if self.password:
            return self.title

        return self.title + " [result]" + (self.text or self.default)

    def _render_input(self) -> Group:
        text = self.text

        if self.password:
            text = "*" * len(self.text)

        # if there's no default value, add a space to keep the cursor visible
        # and, most importantly, in the right place
        default = self.default or " "

        text = f"[text]{text}[/]" if self.text else f"[placeholder]{default }[/]"

        return Group(self.title, text)

    def _refresh(self, show_result: bool = False) -> None:
        renderable = self._render_result() if show_result else self._render_input()

        self._live_render.set_renderable(renderable)

        self._render()

    def _fix_cursor(self, offset: int) -> Control:
        return Control.move_to_column(offset + self._cursor_offset)

    def _render(self):
        self.console.print(
            self._live_render.position_cursor(),
            self._live_render,
            self._fix_cursor(len(self.text)),
        )

    def ask(self) -> str:
        self._refresh()

        while True:
            try:
                key = click.getchar()

                if key == "\r":
                    break

                self._update_text(key)

            except KeyboardInterrupt:
                exit()

            self._refresh()

        self._refresh(show_result=True)

        for _ in range(self._padding_bottom):
            self.console.print()

        return self.text or self.default
