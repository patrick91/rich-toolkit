from typing import List, Tuple

import click
from rich.console import Console, Group, RenderableType
from rich.control import Control, ControlType
from rich.live_render import LiveRender
from rich.style import Style
from rich.text import Text

from rich_toolkit.plain_input import Input


class Form:
    def __init__(self, title: str):
        self.title = title
        self.inputs: List[Input] = []
        self.active_input_index = 1
        self.previous_input_index = 1
        self._live_render = LiveRender("")
        self.console = Console()

    def add_input(
        self, name: str, label: str, placeholder: str, password: bool = False
    ):
        input = Input(console=Console(), password=password)
        input.name = name
        input.label = label
        input.placeholder = placeholder

        self.inputs.append(input)

    def _refresh(self):
        self._live_render.set_renderable(self.render())
        self.console.print(
            *self.move_cursor_at_beginning(),
            self._live_render,
        )
        self.console.print(
            *self.move_cursor_to_active_input(),
        )

    @property
    def _active_input(self) -> Input:
        return self.inputs[self.active_input_index]

    @property
    def _active_input_position(self) -> int:
        return 2 * (self.active_input_index + 1)

    def get_offset_for_input(self, input_index: int) -> int:
        if self._live_render._shape is None:
            return 0

        _, height = self._live_render._shape
        input_position = 2 * (input_index + 1)

        return height - (input_position + 1)

    def get_offset_for_active_input(self) -> int:
        return self.get_offset_for_input(self.active_input_index)

    def move_cursor_to_active_input(self) -> Tuple[Control, ...]:
        move_up = self.get_offset_for_active_input()

        move_cursor = (
            (Control((ControlType.CURSOR_UP, move_up)),) if move_up > 0 else ()
        )

        _cursor_offset = 0
        _cursor_position = self._active_input.cursor_position

        return (Control.move_to_column(_cursor_offset + _cursor_position), *move_cursor)

    def move_cursor_at_beginning(self) -> Tuple[Control, ...]:
        if self._live_render._shape is None:
            return (Control(),)

        original = (self._live_render.position_cursor(),)

        move_down = self.get_offset_for_input(self.previous_input_index)

        if move_down == 0:
            return original

        return (
            Control(
                (ControlType.CURSOR_DOWN, move_down),
            ),
            *original,
        )

    def render(self) -> RenderableType:
        content = []

        for i, input in enumerate(self.inputs):
            if i == self.active_input_index:
                content.append(f"[green]{input.name}[/]")
            else:
                content.append(input.name)
            content.append(input.render_input())

        title = self.title

        if self._live_render._shape is not None:
            title += f" h: {self._live_render._shape[1]} input pos: {self._active_input_position} offset: {self.get_offset_for_active_input()}"

        return Group(
            Text(title, style="bold"),
            *content,
        )

    def run(self):
        self._refresh()
        while True:
            try:
                key = click.getchar()

                self.previous_input_index = self.active_input_index

                if key == "\t":
                    self.active_input_index += 1
                    self.active_input_index %= len(self.inputs)

                elif key == "\r":
                    if self.active_input_index == len(self.inputs) - 1:
                        break
                    else:
                        self.active_input_index += 1
                        self.active_input_index %= len(self.inputs)
                else:
                    # TODO: this should be input.handle_key?
                    self.inputs[self.active_input_index].update_text(key)

                self._refresh()

            except KeyboardInterrupt:
                exit()

        return {input.name: input.text for input in self.inputs}

    def on_update(self, input: Input): ...


# Example with multiple inputs
form = Form(title="Enter your login details")

form.add_input(name="name", label="Name", placeholder="Enter your name")
form.add_input(
    name="password", label="Password", placeholder="Enter your password", password=True
)

results = form.run()

print(results)
