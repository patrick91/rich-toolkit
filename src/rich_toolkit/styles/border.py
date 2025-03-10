from typing import Any

from rich import box
from rich.console import Group, RenderableType
from rich.text import Text

from rich_toolkit.element import CursorOffset, Element
from rich_toolkit.input import Input
from rich_toolkit.menu import Menu
from rich_toolkit.panel import Panel
from rich_toolkit.progress import Progress, ProgressLine

from .base import BaseStyle


class BorderedStyle(BaseStyle):
    def empty_line(self) -> RenderableType:
        return ""

    def decorate(
        self,
        renderable: Element | str,
        is_active: bool = False,
        **metadata: Any,
    ) -> RenderableType:
        title: str | None = None
        validation_message: tuple[str, ...] = ()

        if isinstance(renderable, Input):
            if renderable.valid is False:
                validation_message = (Text("This field is required", style="bold red"),)
            else:
                validation_message = ()

            renderable._should_show_label = False
            renderable._should_show_validation = False

            title = renderable.render_label(is_active=is_active)

        if isinstance(renderable, Menu):
            title = renderable.render_label()

            renderable._should_show_label = False
            renderable._should_show_validation = False

        if isinstance(renderable, Progress):
            title = renderable.title

        if isinstance(renderable, Element):
            rendered = renderable.render(is_active=is_active)
        else:
            rendered = renderable

        if isinstance(renderable, ProgressLine):
            # TODO: call this decorate? or do decorate -> render
            return self.render_progress_log_line(
                rendered,
                index=metadata.get("index", 0),
                max_lines=metadata.get("max_lines", -1),
                total_lines=metadata.get("total_lines", -1),
            )

        content = Group(
            Panel(
                rendered,
                title=title,
                title_align="left",
                highlight=is_active,
                width=50,
                box=box.SQUARE,
            ),
            *validation_message,
        )

        return content

    def get_cursor_offset_for_element(self, element: Element) -> CursorOffset:
        top_offset = element.cursor_offset.top
        left_offset = element.cursor_offset.left + 2

        if isinstance(element, Input) and element.inline:
            # we don't support inline inputs yet in border style
            top_offset += 1

        return CursorOffset(top=top_offset, left=left_offset)
