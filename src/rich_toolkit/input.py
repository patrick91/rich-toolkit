from typing import Any, Tuple

from rich.console import Console, Group, RenderableType
from rich.text import Text

from ._input_handler import TextInputHandler
from .element import CursorOffset, Element
from .styles.base import BaseStyle


# maybe all elements handle input?
class Input(Element, TextInputHandler):
    def __init__(
        self,
        name: str,
        label: str,
        placeholder: str,
        password: bool = False,
        inline: bool = False,
        style: BaseStyle = None,
        **metadata: Any,
    ):
        self.name = name
        self.label = label
        self.placeholder = placeholder
        self.password = password
        self.inline = inline

        self._input_position = None
        self.style = style
        self.metadata = metadata
        self.text = ""
        self.valid = None

        self._height = None
        super().__init__()

    def render(self, is_active: bool = False) -> RenderableType:
        label = self.label

        if is_active:
            label = f"[bold green]{label}[/bold green]"
        elif not self.valid:
            label = f"[bold red]{label}[/bold red]"

        contents = []

        if self.inline:
            contents.append(label + " " + self.render_input())
            self._input_position = 1
        else:
            contents.append(label)
            contents.append(self.render_input())
            self._input_position = 2

        if self.valid is False:
            contents.append(Text("This field is required", style="bold red"))

        self._height = len(contents)

        return Group(*contents)

    @property
    def cursor_offset(self) -> CursorOffset:
        # TODO: why 2?
        top = 1 if self.inline else 2
        left_offset = len(self.label) + 1 if self.inline else 0

        return CursorOffset(top=top, left=self.cursor_left + left_offset)

    @property
    def size(self) -> Tuple[int, int]:
        assert self._height is not None

        return [0, self._height]

    @property
    def should_show_cursor(self) -> bool:
        return True

    def on_blur(self):
        self.valid = bool(self.text)

    def render_input(self) -> RenderableType:
        text = self.text

        if self.password:
            text = "*" * len(self.text)

        # if there's no default value, add a space to keep the cursor visible
        # and, most importantly, in the right place
        placeholder = self.placeholder or " "

        text = f"[text]{text}[/]" if self.text else f"[placeholder]{placeholder}[/]"

        return text

    def ask(self) -> str:
        from .container import Container

        container = Container(style=self.style)
        container.title = self.label

        container.elements = [self]

        container.run()

        return self.text
