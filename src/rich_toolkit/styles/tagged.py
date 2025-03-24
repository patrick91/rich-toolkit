import re
from typing import Any, Dict, Optional

from rich.console import Group, RenderableType
from rich.segment import Segment
from rich.style import Style
from rich.table import Column, Table
from typing_extensions import Literal

from rich_toolkit.container import Container
from rich_toolkit.element import CursorOffset, Element
from rich_toolkit.progress import Progress, ProgressLine

from .base import BaseStyle


def has_emoji(tag: str) -> bool:
    return bool(re.search(r"[\U0001F300-\U0001F9FF]", tag))


class TaggedStyle(BaseStyle):
    block = "█"
    block_length = 5

    def __init__(self, tag_width: int = 12, theme: Optional[Dict[str, str]] = None):
        self.tag_width = tag_width

        theme = theme or {
            "tag.title": "bold",
            "tag": "bold",
        }

        super().__init__(theme=theme)

    def _tag_element(
        self,
        child: RenderableType,
        is_animated: bool = False,
        animation_status: Literal["started", "stopped", "error"] = "started",
        **metadata: Any,
    ) -> RenderableType:
        table = Table.grid(
            # TODO: why do we add 2? :D we probably did this in the previous version
            Column(width=self.tag_width + 2),
            padding=(0, 0, 0, 0),
            collapse_padding=True,
            pad_edge=False,
        )

        style_name = "tag.title" if metadata.get("title", False) else "tag"

        style = self.console.get_style(style_name)

        tag = metadata.get("tag", "")

        right_padding = 0

        # TODO: this is a hack to make the tag width consistent with the emoji width
        # probably won't work with all emojis and if there's more than one emoji
        if has_emoji(tag):
            right_padding = 1

        if tag:
            tag = f" {tag} "

        if is_animated:
            tag = " " * self.block_length
            colors = self._get_animation_colors(
                steps=self.block_length, animation_status=animation_status
            )
            tag_segments = [
                Segment(
                    self.block,
                    style=Style(
                        color=colors[(self.animation_counter + i) % len(colors)]
                    ),
                )
                for i in range(self.block_length)
            ]
        else:
            tag_segments = [Segment(tag, style=style)]

        left_padding = self.tag_width - len(tag) - right_padding
        left_padding = max(0, left_padding)

        left = [Segment(" " * left_padding), *tag_segments]

        table.add_row(Group(*left), Group(child))

        return table

    def render_element(
        self,
        element: Any,
        is_active: bool = False,
        done: bool = False,
        parent: Optional[Element] = None,
        **metadata: Any,
    ) -> RenderableType:
        is_animated = isinstance(element, Progress)
        should_tag = not isinstance(element, (ProgressLine, Container))

        rendered = super().render_element(
            element=element, is_active=is_active, done=done, parent=parent, **metadata
        )

        if should_tag:
            rendered = self._tag_element(
                rendered,
                is_animated=is_animated,
                **metadata,
            )

        return rendered

    def get_cursor_offset_for_element(self, element: Element) -> CursorOffset:
        return CursorOffset(
            top=element.cursor_offset.top,
            left=self.tag_width + element.cursor_offset.left + 2,
        )
