from typing import Any

from rich.console import RenderableType
from rich.segment import Segment
from rich.table import Column, Table

from rich_toolkit._render_wrapper import RenderWrapper
from rich_toolkit.element import CursorOffset
from rich_toolkit.input import InputWithLabel


class TaggedStyle:
    def __init__(self, tag: str, tag_width: int = 12):
        self.tag = tag
        self.tag_width = tag_width

    def _tag_element(self, child: RenderableType) -> Segment:
        table = Table.grid(
            Column(width=self.tag_width),
            padding=(0, 1, 0, 0),
        )

        left_padding = self.tag_width - len(self.tag) - 2
        left_padding = max(0, left_padding)

        left_text = " " * left_padding + "[on red] " + self.tag + " [/on red]"

        table.add_row(left_text, child)

        return table

    def decorate(
        self,
        renderable: InputWithLabel | Any,
        is_active: bool = False,
    ) -> RenderableType:
        rendered = renderable.render(is_active=is_active)

        cursor_offset_left = self.tag_width + 1 + renderable.cursor_offset.left
        cursor_offset_top = renderable.cursor_offset.top

        return RenderWrapper(
            self._tag_element(rendered),
            CursorOffset(
                top=cursor_offset_top,
                left=cursor_offset_left,
            ),
        )
