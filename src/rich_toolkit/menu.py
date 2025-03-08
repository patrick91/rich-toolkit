from typing import Generic, List, Optional, Tuple, TypeVar, cast

import click
from rich import get_console
from rich.console import Console, Group, RenderableType
from rich.control import Control
from rich.segment import ControlType
from rich.text import Text
from typing_extensions import Any, Literal, TypedDict

from ._input_handler import TextInputHandler
from .styles.base import BaseStyle
from .element import Element, CursorOffset

ReturnValue = TypeVar("ReturnValue")


class Option(TypedDict, Generic[ReturnValue]):
    name: str
    value: ReturnValue


class Menu(Generic[ReturnValue], Element, TextInputHandler):
    DOWN_KEYS = [TextInputHandler.DOWN_KEY, "j"]
    UP_KEYS = [TextInputHandler.UP_KEY, "k"]
    LEFT_KEYS = [TextInputHandler.LEFT_KEY, "h"]
    RIGHT_KEYS = [TextInputHandler.RIGHT_KEY, "l"]

    current_selection_char = "●"
    selection_char = "○"
    filter_prompt = "Filter: "

    _should_show_label = True
    _should_show_validation = False

    def __init__(
        self,
        title: str,
        options: List[Option[ReturnValue]],
        inline: bool = False,
        allow_filtering: bool = False,
        *,
        style: Optional[BaseStyle] = None,
        console: Optional[Console] = None,
        cursor_offset: int = 0,
        **metadata: Any,
    ):
        self.console = console or get_console()

        self.title = Text.from_markup(title)
        self.inline = inline
        self.allow_filtering = allow_filtering

        self.selected = 0

        self.metadata = metadata
        self.style = style

        self._options = options

        self._padding_bottom = 1
        self.valid = None

        cursor_offset = cursor_offset + len(self.filter_prompt)

        super().__init__()

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
                if self.text.lower() in option["name"].lower()
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

    def render_label(self) -> RenderableType:
        return self.title

    def render_input(self) -> RenderableType:
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

            is_last = id_ == len(self.options) - 1

            menu.append(
                Text.assemble(
                    prefix,
                    option["name"],
                    separator if not is_last else "",
                    style=style,
                )
            )

        # TODO: inline is not wrapped (maybe that's good?)

        if not self.options:
            # menu.append("No results found", style=self.console.get_style("text"))
            menu = Text("No results found", style=self.console.get_style("text"))

        filter = (
            [
                Text.assemble(
                    (self.filter_prompt, self.console.get_style("text")),
                    (self.text, self.console.get_style("text")),
                    "\n",
                )
            ]
            if self.allow_filtering
            else []
        )

        content = []

        if self._should_show_label:
            content.append(self.render_label())

        content.extend(filter)
        content.append(menu)

        if self.validation_message:
            content.append(Text(""))

            content.append(Text(self.validation_message))

        return Group(*content)

    def render_result(self) -> RenderableType:
        result_text = Text()

        result_text.append(self.title)
        result_text.append(" ")
        result_text.append(
            self.options[self.selected]["name"],
            style=self.console.get_style("result"),
        )

        return result_text

    def is_next_key(self, key: str) -> bool:
        keys = self.RIGHT_KEYS if self.inline else self.DOWN_KEYS

        if self.allow_filtering:
            keys = [keys[0]]

        return key in keys

    def is_prev_key(self, key: str) -> bool:
        keys = self.LEFT_KEYS if self.inline else self.UP_KEYS

        if self.allow_filtering:
            keys = [keys[0]]

        return key in keys

    def handle_key(self, key: str) -> None:
        current_selection: Optional[str] = None

        if self.is_next_key(key):
            self._update_selection("next")
        elif self.is_prev_key(key):
            self._update_selection("prev")
        else:
            super().handle_key(key)

        if self.options:
            current_selection = self.options[self.selected]["name"]

        if current_selection:
            matching_index = next(
                (
                    index
                    for index, option in enumerate(self.options)
                    if option["name"] == current_selection
                ),
                0,
            )

            self.selected = matching_index

    def _handle_enter(self) -> bool:
        if self.allow_filtering and self.text and len(self.options) == 0:
            return False

        return True

    def render(self, is_active: bool = False) -> RenderableType:
        return self.render_input()

    @property
    def validation_message(self) -> str | None:
        if self.valid is False:
            return "This field is required"

        return None

    def on_blur(self):
        self.on_validate()

    def on_validate(self):
        self.valid = len(self.options) > 0

    @property
    def should_show_cursor(self) -> bool:
        return self.allow_filtering

    def ask(self) -> ReturnValue:
        from .container import Container

        container = Container(style=self.style)

        container.elements = [self]

        container.run()

        return self.options[self.selected]["value"]

    @property
    def cursor_offset(self) -> CursorOffset:
        top = 2

        left_offset = len(self.filter_prompt) + self.cursor_left

        return CursorOffset(top=top, left=left_offset)
