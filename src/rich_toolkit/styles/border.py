from typing import Any, Union, Optional

from rich import box
from rich.console import Group, RenderableType
from rich.color import Color
from rich.style import Style
from rich_toolkit.element import CursorOffset, Element
from rich_toolkit._rich_components import Panel

from .base import BaseStyle


class BorderedStyle(BaseStyle):
    box = box.SQUARE

    def empty_line(self) -> RenderableType:
        return ""

    def render(
        self,
        renderable: Union[Element, str],
        is_active: bool = False,
        done: bool = False,
        parent: Optional[Element] = None,
        **metadata: Any,
    ) -> RenderableType:
        from rich_toolkit.input import Input
        from rich_toolkit.menu import Menu
        from rich_toolkit.form import Form
        from rich_toolkit.progress import Progress, ProgressLine

        title: Optional[str] = None
        validation_message: tuple[str, ...] = ()

        # TOOD: from theme
        border_color = Color.parse("white")

        if isinstance(parent, Form) and isinstance(renderable, Element):
            return renderable.render(is_active=is_active, done=done, parent=parent)

        if isinstance(renderable, Input):
            if message := renderable.render_validation_message():
                validation_message = (message,)

            if renderable.valid is False:
                border_color = self.console.get_style("error").color or Color.parse(
                    "red"
                )

            renderable._should_show_label = False
            renderable._should_show_validation = False

            title = renderable.render_label(
                is_active=is_active,
                parent=parent,
            )

        if isinstance(renderable, Menu):
            title = renderable.render_label()

            renderable._should_show_label = False
            renderable._should_show_validation = False

        if isinstance(renderable, Progress):
            title = renderable.title

            border_color = self._get_animation_colors(
                steps=10,
                breathe=True,
                animation_status=metadata.get("animation_status", "started"),
            )[self.animation_counter % 10]

        if isinstance(renderable, Element):
            rendered = renderable.render(
                is_active=is_active,
                done=done,
                parent=parent,
            )

            if renderable._cancelled:
                border_color = self.console.get_style("cancelled").color or Color.parse(
                    "red"
                )

                if title:
                    title = f"[title.cancelled]{title}[/]"

        else:
            rendered = renderable

        if isinstance(renderable, ProgressLine):
            return self.render_progress_log_line(
                rendered,
                index=metadata.get("index", 0),
                max_lines=metadata.get("max_lines", -1),
                total_lines=metadata.get("total_lines", -1),
            )

        if metadata.get("title", False):
            content = rendered
        else:
            content = Group(
                Panel(
                    rendered,
                    title=title,
                    title_align="left",
                    highlight=is_active,
                    width=50,
                    box=self.box,
                    border_style=Style(color=border_color),
                ),
                *validation_message,
            )

        self.animation_counter += 1

        return content

    def get_cursor_offset_for_element(self, element: Element) -> CursorOffset:
        from rich_toolkit.input import Input

        top_offset = element.cursor_offset.top
        left_offset = element.cursor_offset.left + 2

        if isinstance(element, Input) and element.inline:
            # we don't support inline inputs yet in border style
            top_offset += 1

        return CursorOffset(top=top_offset, left=left_offset)
