from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import click
from rich.console import Console, Group, RenderableType
from rich.control import Control, ControlType
from rich.live_render import LiveRender
from rich.style import Style
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


class Form:
    def __init__(self, title: str):
        self.title = title
        self.inputs: List[Input] = []
        self.buttons: List[Button] = []
        self.active_input_index = 1
        self.previous_input_index = 1
        self._live_render = LiveRender("")
        self.console = Console()
        self.active_element_type = "input"  # Can be "input" or "button"
        self.active_button_index = 0

    def add_input(
        self, name: str, label: str, placeholder: str, password: bool = False
    ):
        input = Input(console=Console(), password=password)
        input.name = name
        input.label = label
        input.placeholder = placeholder

        self.inputs.append(input)

    def add_button(self, name: str, label: str, callback: Optional[Callable] = None):
        button = Button(name=name, label=label, callback=callback)
        self.buttons.append(button)

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
    def _active_input(self) -> Input:
        return self.inputs[self.active_input_index]

    @property
    def _active_button(self) -> Button:
        return self.buttons[self.active_button_index]

    @property
    def _active_element(self) -> Union[Input, Button]:
        if self.active_element_type == "input":
            return self._active_input
        else:
            return self._active_button

    @property
    def _active_input_position(self) -> int:
        return 2 * (self.active_input_index + 1)

    @property
    def _active_button_position(self) -> int:
        # Buttons appear after all inputs
        return 2 * (len(self.inputs) + 1) + self.active_button_index

    @property
    def _active_element_position(self) -> int:
        if self.active_element_type == "input":
            return self._active_input_position
        else:
            return self._active_button_position

    def get_offset_for_input(self, input_index: int) -> int:
        if self._live_render._shape is None:
            return 0

        _, height = self._live_render._shape
        input_position = 2 * (input_index + 1)

        return height - (input_position + 1)

    def get_offset_for_button(self, button_index: int) -> int:
        if self._live_render._shape is None:
            return 0

        _, height = self._live_render._shape
        button_position = 2 * (len(self.inputs) + 1) + button_index

        return height - (button_position + 1)

    def get_offset_for_element(self, element_type: str, index: int) -> int:
        if element_type == "input":
            return self.get_offset_for_input(index)
        else:
            return self.get_offset_for_button(index)

    def get_offset_for_active_element(self) -> int:
        if self.active_element_type == "input":
            return self.get_offset_for_input(self.active_input_index)
        else:
            return self.get_offset_for_button(self.active_button_index)

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
        move_down = self.get_offset_for_element(
            self.previous_element_type,
            self.previous_input_index
            if self.previous_element_type == "input"
            else self.previous_button_index,
        )

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
        for i, input in enumerate(self.inputs):
            if i == self.active_input_index and self.active_element_type == "input":
                content.append(f"[green]{input.name}[/]")
            else:
                content.append(input.name)
            content.append(input.render_input())

        # Add a separator if we have both inputs and buttons
        if self.inputs and self.buttons:
            content.append("")

        # Render buttons
        for i, button in enumerate(self.buttons):
            content.append(
                button.render(
                    is_active=(
                        i == self.active_button_index
                        and self.active_element_type == "button"
                    )
                )
            )

        title = self.title

        if self._live_render._shape is not None:
            title += f" h: {self._live_render._shape[1]} pos: {self._active_element_position} offset: {self.get_offset_for_active_element()}"

        return Group(
            Text(title, style="bold"),
            *content,
        )

    def run(self):
        # Initialize previous element tracking
        self.previous_element_type = "input"
        self.previous_input_index = self.active_input_index
        self.previous_button_index = 0

        self._refresh()
        while True:
            try:
                key = click.getchar()

                # Store the previous element state
                self.previous_element_type = self.active_element_type
                self.previous_input_index = self.active_input_index
                self.previous_button_index = self.active_button_index

                if key == "\t":
                    # Tab cycles through all inputs and buttons
                    if self.active_element_type == "input":
                        self.active_input_index += 1
                        if self.active_input_index >= len(self.inputs):
                            # Move to buttons if we've gone through all inputs
                            if self.buttons:
                                self.active_element_type = "button"
                                self.active_input_index = 0
                                self.active_button_index = 0
                            else:
                                # Cycle back to first input if no buttons
                                self.active_input_index = 0
                    else:  # active_element_type == "button"
                        self.active_button_index += 1
                        if self.active_button_index >= len(self.buttons):
                            # Cycle back to first input
                            self.active_element_type = "input"
                            self.active_button_index = 0
                            self.active_input_index = 0

                elif key == "\r":  # Enter key
                    if self.active_element_type == "input":
                        # If on the last input, move to first button or submit
                        if self.active_input_index == len(self.inputs) - 1:
                            if self.buttons:
                                self.active_element_type = "button"
                                self.active_button_index = 0
                            else:
                                break  # Submit form if no buttons
                        else:
                            # Move to next input
                            self.active_input_index += 1
                    else:  # active_element_type == "button"
                        # Activate the button
                        result = self._active_button.activate()
                        if result is True:  # Button indicates form should be submitted
                            break

                else:
                    # Only handle text input when an input is active
                    if self.active_element_type == "input":
                        self.inputs[self.active_input_index].update_text(key)

                self._refresh()

            except KeyboardInterrupt:
                exit()

        # Collect form data
        form_data = {input.name: input.text for input in self.inputs}

        # Add which button was activated, if any
        if self.active_element_type == "button":
            form_data["_button"] = self.buttons[self.active_button_index].name

        return form_data

    def on_update(self, input: Input): ...


# Example with multiple inputs and a button
form = Form(title="Enter your login details")

form.add_input(name="name", label="Name", placeholder="Enter your name")
form.add_input(
    name="password", label="Password", placeholder="Enter your password", password=True
)

# Add a submit button
form.add_button(name="submit", label="Submit")
# Add a cancel button
form.add_button(name="cancel", label="Cancel")

results = form.run()

print(results)
