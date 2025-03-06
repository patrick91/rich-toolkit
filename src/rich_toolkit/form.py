from typing import Any, Callable, Optional

from .button import Button
from .container import Container
from .input import InputWithLabel


class Form(Container):
    def __init__(self, title: str, style: Any):
        super().__init__(style)

        self.title = title

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

    def run(self):
        super().run()

        return self._collect_data()

    def _collect_data(self) -> dict:
        return {
            input.name: input.text
            for input in self.elements
            if isinstance(input, InputWithLabel)
        }
