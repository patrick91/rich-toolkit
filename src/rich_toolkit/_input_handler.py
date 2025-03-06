import string
from typing import Tuple

from rich.control import Control


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
