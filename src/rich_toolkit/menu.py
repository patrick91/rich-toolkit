from typing import Generic, List, Optional, TypeVar

import click
from rich import get_console
from rich.console import Console, Group, RenderableType
from rich.live import Live
from rich.style import Style
from rich.text import Text
from typing_extensions import Any, Literal, TypedDict

from .app_style import AppStyle

ReturnValue = TypeVar("ReturnValue")


class Option(TypedDict, Generic[ReturnValue]):
    name: str
    value: ReturnValue


class Menu(Generic[ReturnValue]):
    current_selection_char = "●"
    selection_char = "○"

    DOWN_KEYS = ["\x1b[B", "j"]
    UP_KEYS = ["\x1b[A", "k"]
    LEFT_KEYS = ["\x1b[D", "h"]
    RIGHT_KEYS = ["\x1b[C", "l"]

    def __init__(
        self,
        title: str,
        options: List[Option[ReturnValue]],
        inline: bool = False,
        *,
        style: AppStyle,
        console: Optional[Console] = None,
        **metadata: Any,
    ):
        self.console = console or get_console()

        self.title = Text.from_markup(title)
        self.options = options
        self.inline = inline

        self.selected = 0

        self.metadata = metadata
        self.style = style

    def get_key(self) -> Optional[Literal["next", "prev", "enter"]]:
        char = click.getchar()

        if char == "\r":
            return "enter"

        next_keys, prev_keys = (
            (self.LEFT_KEYS, self.RIGHT_KEYS)
            if self.inline
            else (self.DOWN_KEYS, self.UP_KEYS)
        )

        if char in next_keys:
            return "next"
        if char in prev_keys:
            return "prev"

        return None

    def _update_selection(self, key: str):
        if key == "next":
            self.selected += 1
        elif key == "prev":
            self.selected -= 1

        if self.selected < 0:
            self.selected = len(self.options) - 1

        if self.selected >= len(self.options):
            self.selected = 0

    def _render_menu(self) -> RenderableType:
        menu = Text(justify="left")

        selected_prefix = Text(self.current_selection_char + " ")
        not_selected_prefix = Text(self.selection_char + " ")

        separator = Text("\t" if self.inline else "\n")

        for id_, option in enumerate(self.options):
            if id_ == self.selected:
                prefix = selected_prefix
                style = self.console.get_style("selected")
            else:
                prefix = not_selected_prefix
                style = self.console.get_style("text")

            menu.append(Text.assemble(prefix, option["name"], separator, style=style))

        menu.rstrip()

        group = Group(self.title, menu)

        return self.style.with_decoration(group, **self.metadata)

    def _render_result(self) -> RenderableType:
        result_text = Text()

        result_text.append(self.title)
        result_text.append(" ")
        result_text.append(
            self.options[self.selected]["name"],
            style=self.console.get_style("result"),
        )

        return self.style.with_decoration(result_text, **self.metadata)

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
