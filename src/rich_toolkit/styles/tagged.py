from typing import Any

from rich.console import Console, Group, RenderableType
from rich.segment import Segment
from rich.table import Column, Table
from rich.theme import Theme

from rich_toolkit.element import CursorOffset, Element
from rich_toolkit.input import Input


class TaggedStyle:
    theme = {
        "tag.title": "black on #A7E3A2",
        "tag": "white on #893AE3",
    }

    # TODO: maybe the theme needs to own the console
    def __init__(self, tag: str, tag_width: int = 12):
        self.tag = tag
        self.tag_width = tag_width

    def _tag_element(self, child: RenderableType, **metadata: Any) -> RenderableType:
        console = Console()
        console.push_theme(Theme(self.theme))

        table = Table.grid(
            Column(width=self.tag_width),
            padding=(0, 0, 0, 0),
            collapse_padding=True,
            pad_edge=False,
        )

        style_name = "tag.title" if metadata.get("title", False) else "tag"

        style = console.get_style(style_name)

        tag = metadata.get("tag", self.tag)

        if tag:
            tag = f" {tag} "

        left_padding = self.tag_width - len(tag) - 2
        left_padding = max(0, left_padding)

        left = [Segment(" " * left_padding), Segment(tag, style=style)]

        table.add_row(Group(*left), child)

        console.pop_theme()

        return table

    def empty_line(self) -> RenderableType:
        return ""

    def decorate(
        self,
        renderable: Input | Any,
        is_active: bool = False,
        **metadata: Any,
    ) -> RenderableType:
        if isinstance(renderable, str):
            rendered = renderable
        else:
            rendered = renderable.render(is_active=is_active)

            # cursor_offset_left = self.tag_width + renderable.cursor_offset.left
            # cursor_offset_top = renderable.cursor_offset.top

        return self._tag_element(rendered, **metadata)

    def get_cursor_offset_for_element(self, element: Element) -> CursorOffset:
        return CursorOffset(
            top=element.cursor_offset.top,
            left=self.tag_width + element.cursor_offset.left,
        )
