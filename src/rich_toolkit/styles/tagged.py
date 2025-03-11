import re
from typing import Any

from rich.console import Console, Group, RenderableType
from rich.segment import Segment
from rich.table import Column, Table
from rich.theme import Theme

from rich_toolkit.element import CursorOffset, Element
from rich_toolkit.progress import ProgressLine

from .base import BaseStyle


def has_emoji(tag: str) -> bool:
    return bool(re.search(r"[\U0001F300-\U0001F9FF]", tag))


class TaggedStyle(BaseStyle):
    theme = {
        "tag.title": "black on #A7E3A2",
        "tag": "white on #893AE3",
    }

    # TODO: maybe the theme needs to own the console
    def __init__(self, tag_width: int = 12):
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

        tag = metadata.get("tag", "")

        if tag:
            tag = f" {tag} "

        right_padding = 2

        if has_emoji(tag):
            right_padding = 3

        left_padding = self.tag_width - len(tag) - right_padding
        left_padding = max(0, left_padding)

        left = [Segment(" " * left_padding), Segment(tag, style=style)]

        table.add_row(Group(*left), Group(child))

        console.pop_theme()

        return table

    def decorate(
        self,
        renderable: Element | str,
        is_active: bool = False,
        done: bool = False,
        **metadata: Any,
    ) -> RenderableType:
        if isinstance(renderable, Element):
            rendered = renderable.render(is_active=is_active, done=done)
        else:
            rendered = renderable

        if isinstance(renderable, ProgressLine):
            return self.render_progress_log_line(
                rendered,
                index=metadata.get("index", 0),
                max_lines=metadata.get("max_lines", -1),
                total_lines=metadata.get("total_lines", -1),
            )

        return self._tag_element(rendered, **metadata)

    def get_cursor_offset_for_element(self, element: Element) -> CursorOffset:
        return CursorOffset(
            top=element.cursor_offset.top,
            left=self.tag_width + element.cursor_offset.left,
        )
