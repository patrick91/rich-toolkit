from typing import Any, Callable, List, Optional, Tuple, Union

import click
from rich.console import Console, Group, RenderableType
from rich.control import Control, ControlType
from rich.live_render import LiveRender
from rich.text import Text

from rich_toolkit.plain_input import Input


class Button:
    def __init__(self, name: str, label: str, callback: Optional[Callable] = None):
        self.name = name
        self.label = label
        self.callback = callback
        self.cursor_position = 0  # For compatibility with Input

    @property
    def should_show_cursor(self) -> bool:
        return False

    def render(self, is_active: bool = False) -> RenderableType:
        style = "bold green" if is_active else "bold"
        return Text(f"[ {self.label} ]", style=style)

    def activate(self) -> Any:
        if self.callback:
            return self.callback()
        return True

    @property
    def size(self) -> Tuple[int, int]:
        return [0, 1]


class InputWithLabel:
    def __init__(
        self,
        name: str,
        label: str,
        placeholder: str,
        password: bool = False,
        inline: bool = False,
    ):
        self.name = name
        self.label = label
        self.placeholder = placeholder
        self.password = password
        self.inline = inline
        self.input = Input(console=Console(), password=password)

    def render(self, is_active: bool = False) -> RenderableType:
        if self.inline:
            return self.input.render(is_active=is_active)
        else:
            return Group(
                Text(f"[ {self.label} ]", style="bold green" if is_active else "bold"),
                self.input.render(is_active=is_active),
            )

    @property
    def should_show_cursor(self) -> bool:
        return self.input.should_show_cursor

    @property
    def cursor_position(self) -> int:
        return self.input.cursor_position

    @property
    def text(self) -> str:
        return self.input.text

    @property
    def size(self) -> Tuple[int, int]:
        if self.inline:
            return [0, 1]
        else:
            return [0, 2]

    def update_text(self, text: str):
        self.input.update_text(text)


class Form:
    def __init__(self, title: str):
        self.title = title
        self.elements: List[Input | Button] = []
        self.active_element_index = 0
        self.previous_element_index = 0
        self._live_render = LiveRender("")
        self.console = Console()

    def add_input(
        self,
        name: str,
        label: str,
        placeholder: str,
        password: bool = False,
        inline: bool = False,
    ):
        input = InputWithLabel(name, label, placeholder, password, inline)

        self.elements.append(input)

    def add_button(self, name: str, label: str, callback: Optional[Callable] = None):
        button = Button(name=name, label=label, callback=callback)
        self.elements.append(button)

    def _refresh(self):
        self._live_render.set_renderable(self.render())

        self.console.print(
            Control.show_cursor(self._active_element.should_show_cursor),
            *self.move_cursor_at_beginning(),
            self._live_render,
        )
        self.console.print(
            *self.move_cursor_to_active_element(),
        )

    @property
    def _active_element(self) -> Union[Input, Button]:
        return self.elements[self.active_element_index]

    def _get_element_position(self, element_index: int) -> int:
        position = 0

        for i in range(element_index + 1):
            position += self.elements[i].size[1]

        return position

    @property
    def _active_element_position(self) -> int:
        return self._get_element_position(self.active_element_index)

    def get_offset_for_element(self, element_index: int) -> int:
        if self._live_render._shape is None:
            return 0

        position = self._get_element_position(element_index)

        _, height = self._live_render._shape

        return height - position

    def get_offset_for_active_element(self) -> int:
        return self.get_offset_for_element(self.active_element_index)

    def move_cursor_to_active_element(self) -> Tuple[Control, ...]:
        move_up = self.get_offset_for_active_element()

        move_cursor = (
            (Control((ControlType.CURSOR_UP, move_up)),) if move_up > 0 else ()
        )

        _cursor_offset = 0
        _cursor_position = self._active_element.cursor_position

        return (Control.move_to_column(_cursor_offset + _cursor_position), *move_cursor)

    def move_cursor_at_beginning(self) -> Tuple[Control, ...]:
        if self._live_render._shape is None:
            return (Control(),)

        original = (self._live_render.position_cursor(),)

        # Use the previous element type and index for cursor positioning
        move_down = self.get_offset_for_element(self.previous_element_index)

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

        # Render inputs
        for i, element in enumerate(self.elements):
            content.append(element.render(is_active=i == self.active_element_index))

        title = self.title

        if self._live_render._shape is not None:
            title += f" h: {self._live_render._shape[1]} offset: {self.get_offset_for_active_element()}"

        return Group(
            # Text(title, style="bold"),
            *content,
        )

    def run(self):
        self._refresh()
        while True:
            try:
                key = click.getchar()

                # Store the previous element state
                self.previous_element_index = self.active_element_index

                if key == "\t":
                    self.active_element_index += 1
                    if self.active_element_index >= len(self.elements):
                        self.active_element_index = 0

                elif key == "\r":  # Enter key
                    break

                else:
                    if hasattr(self._active_element, "update_text"):
                        # TODO: this should be handle key
                        self._active_element.update_text(key)

                self._refresh()

            except KeyboardInterrupt:
                exit()

        # Collect form data
        form_data = {input.name: input.text for input in self.inputs}

        # Add which button was activated, if any
        if self.active_element_type == "button":
            form_data["_button"] = self.buttons[self.active_button_index].name

        return form_data


# Example with multiple inputs and a button
form = Form(title="Enter your login details")

form.add_button(name="AI", label="AI")

form.add_input(name="name", label="Name", placeholder="Enter your name")
form.add_input(
    name="password", label="Password", placeholder="Enter your password", password=True
)

# Add a submit button
form.add_button(name="submit", label="Submit")
form.add_input(name="email", label="Email", placeholder="Enter your email", inline=True)

# Add a cancel button
form.add_button(name="cancel", label="Cancel")

results = form.run()

print(results)
