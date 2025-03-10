from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rich.console import Group, RenderableType

from ._input_handler import TextInputHandler
from .element import CursorOffset, Element

if TYPE_CHECKING:
    from .styles.base import BaseStyle


class Input(Element, TextInputHandler):
    label: str | None = None
    placeholder: str | None = None
    _should_show_label: bool = True
    _should_show_validation: bool = True

    def __init__(
        self,
        # TODO: do we need name?
        name: str,
        label: str | None = None,
        placeholder: str | None = None,
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

        self.style = style
        self.metadata = metadata
        self.text = ""
        self.valid = None

        super().__init__(**metadata)

    def render_label(self, is_active: bool = False) -> str | None:
        label: str | None = None

        if self.label:
            label = self.label

            if is_active:
                label = f"[bold green]{label}[/bold green]"
            elif not self.valid:
                label = f"[bold red]{label}[/bold red]"

        return label

    def render_validation_message(self) -> str | None:
        if self.valid is False:
            return f"[bold red]{self.validation_message}[/bold red]"

        return None

    def render(self, is_active: bool = False) -> RenderableType:
        label = self.render_label(is_active) if self._should_show_label else None
        text = self.render_input()

        contents = []

        if self.inline:
            if label:
                text = f"{label} {text}"

            contents.append(text)
        else:
            if label:
                contents.append(label)

            contents.append(text)

        if self.validation_message and self._should_show_validation:
            contents.append(self.render_validation_message())

        self._height = len(contents)

        return Group(*contents)

    @property
    def validation_message(self) -> str | None:
        if self.valid is False:
            return "This field is required"

        return None

    @property
    def cursor_offset(self) -> CursorOffset:
        top = 1 if self.inline else 2

        left_offset = 0

        if self.inline and self.label and self._should_show_label:
            left_offset = len(self.label) + 1

        return CursorOffset(top=top, left=self.cursor_left + left_offset)

    @property
    def should_show_cursor(self) -> bool:
        return True

    def on_blur(self):
        self.on_validate()

    def on_validate(self):
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
