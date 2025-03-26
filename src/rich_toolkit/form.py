from typing import Any, Callable, Optional

from rich_toolkit.styles import BaseStyle

from .button import Button
from .container import Container
from .input import Input


class Form(Container):
    def __init__(self, title: str, style: BaseStyle):
        super().__init__(style)

        self.title = title

    def add_input(
        self,
        name: str,
        label: str,
        placeholder: str,
        password: bool = False,
        inline: bool = False,
        required: bool = False,
        **metadata: Any,
    ):
        input = Input(
            label=label,
            placeholder=placeholder,
            name=name,
            password=password,
            inline=inline,
            required=required,
            **metadata,
        )

        self.elements.append(input)

    def add_button(
        self,
        name: str,
        label: str,
        callback: Optional[Callable] = None,
        **metadata: Any,
    ):
        button = Button(name=name, label=label, callback=callback, **metadata)
        self.elements.append(button)

    def run(self):
        super().run()

        return self._collect_data()

    def handle_enter_key(self) -> bool:
        all_valid = True

        for element in self.elements:
            if isinstance(element, Input):
                element.on_validate()

                if element.valid is False:
                    all_valid = False

        return all_valid

    def _collect_data(self) -> dict:
        return {
            input.name: input.text
            for input in self.elements
            if isinstance(input, Input)
        }
