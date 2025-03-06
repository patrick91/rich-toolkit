# this will become the input class, but for now we make a copy
# so we don't fear to change stuff
import string
from typing import Any, Optional, Tuple

import click
from rich.console import Console, Group, RenderableType
from rich.control import Control
from rich.live_render import LiveRender

from rich_toolkit.styles.base import BaseStyle


class TextInputHandler:
    DOWN_KEY = "\x1b[B"
    UP_KEY = "\x1b[A"
    LEFT_KEY = "\x1b[D"
    RIGHT_KEY = "\x1b[C"
    BACKSPACE_KEY = "\x7f"
    DELETE_KEY = "\x1b[3~"

    def __init__(self, cursor_offset: int = 0):
        self.text = ""
        self.cursor_left = 0
        self._cursor_offset = cursor_offset

    def _move_cursor_left(self) -> None:
        self.cursor_left = max(0, self.cursor_left - 1)

    def _move_cursor_right(self) -> None:
        self.cursor_left = min(len(self.text), self.cursor_left + 1)

    def _insert_char(self, char: str) -> None:
        self.text = self.text[: self.cursor_left] + char + self.text[self.cursor_left :]
        self._move_cursor_right()

    def _delete_char(self) -> None:
        if self.cursor_left == 0:
            return

        self.text = self.text[: self.cursor_left - 1] + self.text[self.cursor_left :]
        self._move_cursor_left()

    def _delete_forward(self) -> None:
        if self.cursor_left == len(self.text):
            return

        self.text = self.text[: self.cursor_left] + self.text[self.cursor_left + 1 :]

    def update_text(self, text: str) -> None:
        if text == self.BACKSPACE_KEY:
            self._delete_char()
        elif text == self.DELETE_KEY:
            self._delete_forward()
        elif text == self.LEFT_KEY:
            self._move_cursor_left()
        elif text == self.RIGHT_KEY:
            self._move_cursor_right()
        elif text in (self.UP_KEY, self.DOWN_KEY):
            pass
        else:
            for char in text:
                if char in string.printable:
                    self._insert_char(char)

    def fix_cursor(self) -> Tuple[Control, ...]:
        return (Control.move_to_column(self._cursor_offset + self.cursor_left),)


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
