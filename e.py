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
        self.active_input_index = 0
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
            *self.position_cursor(),
            self._live_render,
            *self.fix_cursor(),
        )

    @property
    def _active_input(self) -> Input:
        return self.inputs[self.active_input_index]

    @property
    def _active_input_position(self) -> int:
        title_size = 1
        input_size = 2
        return title_size + input_size * (self.active_input_index + 1)

    def fix_cursor(self) -> Tuple[Control, ...]:
        """Fixes the position of cursor after rendering the container.

        It moves the cursor up based on the current focused container (? input actually)
        """
        move_up = self._active_input_position

        # TODO: this is potentially problematic, as we need the size of the container
        # on *first* render...
        if self._live_render._shape is None:
            return ()

        _, height = self._live_render._shape

        move_cursor = (
            (Control((ControlType.CURSOR_UP, height - move_up)),) if move_up > 0 else ()
        )

        _cursor_offset = 0
        _cursor_position = self._active_input.cursor_position

        return (Control.move_to_column(_cursor_offset + _cursor_position), *move_cursor)

    def position_cursor(self) -> Tuple[Control, ...]:
        """Positions the cursor at the end of the container.

        It moves the cursor up based on the size of the container.
        It does by taking into account the size of the container.

        We use the shape of the container to calculate the number of times we
        need to move the cursor up, we do this because the children of the
        container are dynamic and we need the current size of the container
        to calculate the correct position of the cursor.

        * Current size means the previous size of the container, but I say
        current because we haven't rendered the updated container yet :)
        """
        original = (self._live_render.position_cursor(),)

        if self._live_render._shape is None:
            return original

        _, height = self._live_render._shape

        move_down = self._active_input_position

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

        return Group(
            Text(self.title, style="bold"),
            *content,
        )

    def run(self):
        self._refresh()
        while True:
            try:
                key = click.getchar()

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
