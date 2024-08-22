import string

import click
from rich.console import Console, Group, RenderableType
from rich.control import Control
from rich.live_render import LiveRender
from rich.text import Text

from .row import RowWithTitle


class Input:
    def __init__(self, console: Console, tag: str, title: str, default: str = ""):
        self.tag = tag
        self.title = title
        self.default = default
        self.text = ""

        self.console = console

        self._live_render = LiveRender("")
        self._moved_up = False
        self._padding_bottom = 1

    def _update_text(self, char: str) -> None:
        if char == "\x7f":
            self.text = self.text[:-1]
        elif char in string.printable:
            self.text += char

    def _render_result(self) -> RenderableType:
        return RowWithTitle(
            self.tag, self.title + " [#aaaaaa]" + (self.text or self.default)
        )

    def _render_input(self) -> RenderableType:
        text = (
            f"[#ffffff]{self.text}[/]" if self.text else f"[#aaaaaa]{self.default}[/]"
        )

        return RowWithTitle(
            self.tag,
            Group(self.title, text),
        )

    def _refresh(self, show_result: bool = False) -> None:
        renderable = self._render_result() if show_result else self._render_input()

        self._live_render.set_renderable(renderable)

        self._render()

    def _render(self):
        move_cursor = [
            Control.move(0, -1 * self._padding_bottom),
            Control.move_to_column(12 + len(self.text)),
        ]

        self.console.print(
            self._live_render.position_cursor(),
            self._live_render,
            [Text() for _ in range(self._padding_bottom)],
            *move_cursor,
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

        # adds a new line after the result
        self.console.print()

        for _ in range(self._padding_bottom):
            self.console.print()

        return self.text or self.default
