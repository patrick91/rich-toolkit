from typing import Generic, List, Optional, TypeVar, cast

import click
from rich import get_console
from rich.console import Console, Group, RenderableType
from rich.control import Control
from rich.segment import ControlType
from rich.text import Text
from rich.live_render import LiveRender
from typing_extensions import Any, Literal, TypedDict

from .styles.base import BaseStyle
from .input import TextInputHandler

ReturnValue = TypeVar("ReturnValue")


class Option(TypedDict, Generic[ReturnValue]):
    name: str
    value: ReturnValue


class Menu(Generic[ReturnValue], TextInputHandler):
    DOWN_KEYS = [TextInputHandler.DOWN_KEY, "j"]
    UP_KEYS = [TextInputHandler.UP_KEY, "k"]
    LEFT_KEYS = [TextInputHandler.LEFT_KEY, "h"]
    RIGHT_KEYS = [TextInputHandler.RIGHT_KEY, "l"]

    current_selection_char = "●"
    selection_char = "○"
    filter_prompt = "Filter: "

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

        # TODO: this can be in a base class (see input)
        if style is None:
            self._live_render = LiveRender("")
        else:
            self._live_render = style.decorate_class(LiveRender, **metadata)("")

        self._padding_bottom = 1

        cursor_offset = cursor_offset + len(self.filter_prompt)

        super().__init__(cursor_offset=cursor_offset)

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

        # TODO: inline is not wrapped (maybe that's good?)

        if not self.options:
            # menu.append("No results found", style=self.console.get_style("text"))
            menu = Text("No results found\n\n", style=self.console.get_style("text"))

        h = 0
        if self._live_render._shape is not None:
            _, h = self._live_render._shape

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

        return Group(self.title, *filter, *menu)

    def _render_result(self) -> RenderableType:
        result_text = Text()

        result_text.append(self.title)
        result_text.append(" ")
        result_text.append(
            self.options[self.selected]["name"],
            style=self.console.get_style("result"),
        )

        return result_text

    def update_text(self, text: str) -> None:
        current_selection: Optional[str] = None

        if self.options:
            current_selection = self.options[self.selected]["name"]

        super().update_text(text)

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

    def move_cursor(self) -> Control:
        if self.allow_filtering:
            height = len(self.options) + 1 if self.options else 2

            return Control((ControlType.CURSOR_UP, height))

        return Control()

    def reposition_cursor(self) -> Control:
        if self.allow_filtering:
            if self._live_render._shape is None:
                return Control()

            _, height = self._live_render._shape

            move_down = height - 2

            return Control(
                (ControlType.CURSOR_DOWN, move_down),
                ControlType.CARRIAGE_RETURN,
                (ControlType.ERASE_IN_LINE, 2),
                *(
                    (
                        (ControlType.CURSOR_UP, 1),
                        (ControlType.ERASE_IN_LINE, 2),
                    )
                    * (height - 1)
                ),
            )

        return self._live_render.position_cursor()

    def _render(self, show_result: bool = False) -> None:
        self.console.print(
            Control.show_cursor(True if self.allow_filtering else False),
            self.reposition_cursor(),
            self._live_render,
        )

        if not show_result:
            self.console.print(
                self.fix_cursor(),
                self.move_cursor(),
            )

    def _refresh(self, show_result: bool = False) -> None:
        renderable = self._render_result() if show_result else self._render_menu()

        self._live_render.set_renderable(renderable)

        self._render(show_result)

    def ask(self) -> ReturnValue:
        self._refresh()

        while True:
            try:
                key = self.get_key()

                if key == "enter":
                    if self._handle_enter():
                        break

                elif key is not None:
                    if key in ["next", "prev"]:
                        key = cast(Literal["next", "prev"], key)
                        self._update_selection(key)
                    else:
                        self.update_text(key)

            except KeyboardInterrupt:
                exit()

            self._refresh()

        self._refresh(show_result=True)

        for _ in range(self._padding_bottom):
            self.console.print()

        return self.options[self.selected]["value"]
