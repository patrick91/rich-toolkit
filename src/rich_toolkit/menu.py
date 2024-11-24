from typing import Generic, List, Optional, TypeVar, cast
import string

import click
from rich import get_console
from rich.console import Console, Group, RenderableType
from rich.live import Live
from rich.text import Text
from typing_extensions import Any, Literal, TypedDict

from .styles.base import BaseStyle

ReturnValue = TypeVar("ReturnValue")


class Option(TypedDict, Generic[ReturnValue]):
    name: str
    value: ReturnValue


class Menu(Generic[ReturnValue]):
    current_selection_char = "●"
    selection_char = "○"

    DOWN_KEY = "\x1b[B"
    UP_KEY = "\x1b[A"
    LEFT_KEY = "\x1b[D"
    RIGHT_KEY = "\x1b[C"

    DOWN_KEYS = [DOWN_KEY, "j"]
    UP_KEYS = [UP_KEY, "k"]
    LEFT_KEYS = [LEFT_KEY, "h"]
    RIGHT_KEYS = [RIGHT_KEY, "l"]

    def __init__(
        self,
        title: str,
        options: List[Option[ReturnValue]],
        inline: bool = False,
        allow_filtering: bool = False,
        *,
        style: Optional[BaseStyle] = None,
        console: Optional[Console] = None,
        **metadata: Any,
    ):
        self.console = console or get_console()

        self.title = Text.from_markup(title)
        self.inline = inline
        self.allow_filtering = allow_filtering

        self.selected = 0

        self.metadata = metadata
        self.style = style

        self._current_filter = ""
        self._options = options

    def get_key(self) -> Optional[str]:
        char = click.getchar()

        if char == "\r":
            return "enter"

        if self.allow_filtering:
            left_keys, right_keys = [[self.LEFT_KEY], [self.RIGHT_KEY]]
            down_keys, up_keys = [[self.DOWN_KEY], [self.UP_KEY]]
        else:
            left_keys, right_keys = self.LEFT_KEYS, self.RIGHT_KEYS
            down_keys, up_keys = self.DOWN_KEYS, self.UP_KEYS

        next_keys, prev_keys = (
            (right_keys, left_keys) if self.inline else (down_keys, up_keys)
        )

        if char in next_keys:
            return "next"
        if char in prev_keys:
            return "prev"

        if self.allow_filtering:
            return char

        return None

    @property
    def options(self) -> List[Option[ReturnValue]]:
        if self.allow_filtering:
            return [
                option
                for option in self._options
                if self._current_filter.lower() in option["name"].lower()
            ]

        return self._options

    def _update_selection(self, key: Literal["next", "prev"]) -> None:
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

        filter = (
            [
                Text.assemble(
                    ("Filter: ", self.console.get_style("text")),
                    (self._current_filter, self.console.get_style("text")),
                    "\n",
                )
            ]
            if self.allow_filtering
            else []
        )

        group = Group(self.title, *filter, menu)

        if self.style is None:
            return group

        return self.style.with_decoration(group, **self.metadata)

    def _render_result(self) -> RenderableType:
        result_text = Text()

        result_text.append(self.title)
        result_text.append(" ")
        result_text.append(
            self.options[self.selected]["name"],
            style=self.console.get_style("result"),
        )

        if self.style is None:
            return result_text

        return self.style.with_decoration(result_text, **self.metadata)

    # TODO: in future reuse Input's functionality for this
    def _update_filter(self, char: str) -> None:
        if char == "\x7f":
            self._current_filter = self._current_filter[:-1]
        elif char in string.printable:
            self._current_filter += char

    def _handle_enter(self) -> bool:
        if self.allow_filtering and self._current_filter and len(self.options) == 0:
            return False

        return True

    def ask(self) -> ReturnValue:
        with Live(
            self._render_menu(), auto_refresh=False, console=self.console
        ) as live:
            while True:
                try:
                    key = self.get_key()

                    if key == "enter" and self._handle_enter():
                        break

                    if key is not None:
                        if key in ["next", "prev"]:
                            key = cast(Literal["next", "prev"], key)
                            self._update_selection(key)
                        else:
                            self._update_filter(key)

                        live.update(self._render_menu(), refresh=True)
                except KeyboardInterrupt:
                    exit()

            live.update(self._render_result(), refresh=True)

        return self.options[self.selected]["value"]
