from typing import Tuple

from rich.console import Console, Group, RenderableType
from rich.text import Text

from .element import CursorOffset, Element
from .plain_input import Input
from .styles.base import BaseStyle


class InputWithLabel(Element):
    def __init__(
        self,
        name: str,
        label: str,
        placeholder: str,
        password: bool = False,
        inline: bool = False,
        style: BaseStyle = None,
    ):
        self.name = name
        self.label = label
        self.placeholder = placeholder
        self.password = password
        self.inline = inline
        self.input = Input(console=Console(), password=password)

        self._input_position = None
        self.style = style

        if inline:
            self.input._cursor_offset = len(self.label) + 1

        self._height = None

    def render(self, is_active: bool = False) -> RenderableType:
        label = self.label

        if is_active:
            label = f"[bold green]{label}[/bold green]"
        elif not self.input.valid:
            label = f"[bold red]{label}[/bold red]"

        contents = []

        if self.inline:
            contents.append(label + " " + self.input.render(is_active=is_active))
            self._input_position = 1
        else:
            contents.append(label)
            contents.append(self.input.render(is_active=is_active))
            self._input_position = 2

        if self.input.valid is False:
            contents.append(Text("This field is required", style="bold red"))

        self._height = len(contents)

        return Group(*contents)

    def on_blur(self):
        self.input.on_blur()

    @property
    def should_show_cursor(self) -> bool:
        return self.input.should_show_cursor

    @property
    def cursor_left(self) -> int:
        return self.input.cursor_left

    @property
    def cursor_offset(self) -> CursorOffset:
        # TODO: why 2?
        top = 1 if self.inline else 2
        left_offset = len(self.label) + 1 if self.inline else 0

        return CursorOffset(top=top, left=self.input.cursor_left + left_offset)

    @property
    def text(self) -> str:
        return self.input.text

    @property
    def size(self) -> Tuple[int, int]:
        assert self._height is not None

        return [0, self._height]

    def update_text(self, text: str):
        self.input.update_text(text)

    def ask(self) -> str:
        from .container import Container

        container = Container(style=self.style)
        container.title = self.label

        container.elements = [self]

        return container.run()
