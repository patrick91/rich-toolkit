from typing import Generic, List, Optional, TypeVar

import click
from rich import get_console
from rich.console import Console, Group, RenderableType
from rich.live import Live
from rich.padding import Padding
from rich.style import Style
from rich.text import Text
from typing_extensions import Literal, TypedDict

from .row import RowWithTitle

ReturnValue = TypeVar("ReturnValue")


class Option(TypedDict, Generic[ReturnValue]):
    name: str
    value: ReturnValue


class Menu(Generic[ReturnValue]):
    selection_char = "❯"

    DOWN_KEYS = ["\x1b[B", "j"]
    UP_KEYS = ["\x1b[A", "k"]

    def __init__(
        self,
        tag: str,
        title: str,
        options: List[Option[ReturnValue]],
        *,
        console: Optional[Console] = None,
    ):
        self.console = console or get_console()

        self.tag = tag
        self.title = Text.from_markup(title)
        self.options = options

        self.selected = 0

        self.row_style = Style()
        self.selected_style = Style(color="#079587")

        self.value_style = Style(color="#9e9e9e")

    def get_key(self) -> Optional[Literal["down", "up", "enter"]]:
        char = click.getchar()

        if char == "\r":
            return "enter"

        if char in self.DOWN_KEYS:
            return "down"

        if char in self.UP_KEYS:
            return "up"

        return None

    def _update_selection(self, key: str):
        if key == "down":
            self.selected += 1
        elif key == "up":
            self.selected -= 1

        if self.selected < 0:
            self.selected = len(self.options) - 1

        if self.selected >= len(self.options):
            self.selected = 0

    def _render_menu(self) -> RenderableType:
        menu = Text(justify="left")

        selected_prefix = Text(self.selection_char + " ")
        not_selected_prefix = Text(" " * (len(self.selection_char) + 1))

        for id_, option in enumerate(self.options):
            if id_ == self.selected:
                prefix = selected_prefix
                style = self.selected_style
            else:
                prefix = not_selected_prefix
                style = self.row_style

            menu.append(Text.assemble(prefix, option["name"], "\n", style=style))

        menu.rstrip()

        group = Group(self.title, menu)

        return Padding(RowWithTitle(self.tag, group), (0, 0, 2, 0))

    def _render_result(self) -> RenderableType:
        result_text = Text()

        result_text.append(self.title)
        result_text.append(" ")
        result_text.append(self.options[self.selected]["name"], style=self.value_style)

        return RowWithTitle(self.tag, result_text)

    def ask(self) -> ReturnValue:
        with Live(
            self._render_menu(), auto_refresh=False, console=self.console
        ) as live:
            while True:
                try:
                    key = self.get_key()

                    if key == "enter":
                        break

                    if key is not None:
                        self._update_selection(key)

                        live.update(self._render_menu(), refresh=True)
                except KeyboardInterrupt:
                    exit()

            live.update(self._render_result(), refresh=True)

        return self.options[self.selected]["value"]
