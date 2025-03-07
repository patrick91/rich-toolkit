from typing import Any

from rich import box
from rich.console import Group, RenderableType
from rich.text import Text

from rich_toolkit.element import CursorOffset, Element
from rich_toolkit.input import Input
from rich_toolkit.panel import Panel
from rich_toolkit.streaming_container import StreamingContainer

from .base import BaseStyle


class BorderedStyle(BaseStyle):
    def empty_line(self) -> RenderableType:
        return ""

    def decorate(
        self,
        renderable: Element,
        is_active: bool = False,
        **metadata: Any,
    ) -> RenderableType:
        if isinstance(renderable, str):
            return renderable

        if isinstance(renderable, StreamingContainer):
            return Group(
                Panel.fit(Group(*renderable.logs), title="LOL", title_align="left"),
                renderable.footer_content,
            )

        if isinstance(renderable, Input):
            if renderable.valid is False:
                validation_message = (Text("This field is required", style="bold red"),)
            else:
                validation_message = ()

            renderable._should_show_label = False

            content = Group(
                Panel(
                    renderable.render(is_active=is_active),
                    highlight=is_active,
                    title=renderable.label,
                    title_align="left",
                    width=50,
                    box=box.SQUARE,
                ),
                *validation_message,
            )

            return content

        return renderable.render(is_active=is_active)

    def get_cursor_offset_for_element(self, element: Element) -> CursorOffset:
        top_offset = element.cursor_offset.top
        left_offset = element.cursor_offset.left + 2

        if isinstance(element, Input) and element.inline:
            # we don't support inline inputs yet in border style
            top_offset += 1

        return CursorOffset(top=top_offset, left=left_offset)
