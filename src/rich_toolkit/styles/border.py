from typing import Any, Optional, Union

from rich import box
from rich.color import Color
from rich.console import Group, RenderableType
from rich.style import Style
from rich.text import Text

from rich_toolkit._rich_components import Panel
from rich_toolkit.element import CursorOffset, Element
from rich_toolkit.input import Input
from rich_toolkit.menu import Menu

from .base import BaseStyle


class BorderedStyle(BaseStyle):
    box = box.SQUARE

    def empty_line(self) -> RenderableType:
        return ""

    def render_input(
        self,
        element: Input,
        is_active: bool = False,
        done: bool = False,
        parent: Optional[Element] = None,
        **metadata: Any,
    ) -> RenderableType:
        validation_message: tuple[str, ...] = ()

        if message := self.render_validation_message(element):
            validation_message = (message,)

        if element.valid is False:
            border_color = self.console.get_style("error").color or Color.parse("red")

        title = self.render_input_label(
            element,
            is_active=is_active,
            parent=parent,
        )

        border_color = Color.parse("white")

        return Group(
            Panel(
                self.render_input_value(element, is_active=is_active, parent=parent),
                title=title,
                title_align="left",
                highlight=is_active,
                width=50,
                box=self.box,
                border_style=Style(color=border_color),
            ),
            *validation_message,
        )

    def render_menu(
        self,
        element: Menu,
        is_active: bool = False,
        done: bool = False,
        parent: Optional[Element] = None,
        **metadata: Any,
    ) -> RenderableType:
        menu = Text(justify="left")

        selected_prefix = Text(element.current_selection_char + " ")
        not_selected_prefix = Text(element.selection_char + " ")

        separator = Text("\t" if element.inline else "\n")

        if done:
            result_content = Text()

            result_content.append(
                self.render_input_label(element, is_active=is_active, parent=parent)
            )
            result_content.append(" ")

            result_content.append(
                element.options[element.selected]["name"],
                style=self.console.get_style("result"),
            )

            return result_content

        for id_, option in enumerate(element.options):
            if id_ == element.selected:
                prefix = selected_prefix
                style = self.console.get_style("selected")
            else:
                prefix = not_selected_prefix
                style = self.console.get_style("text")

            is_last = id_ == len(element.options) - 1

            menu.append(
                Text.assemble(
                    prefix,
                    option["name"],
                    separator if not is_last else "",
                    style=style,
                )
            )

        if not element.options:
            menu = Text("No results found", style=self.console.get_style("text"))

        filter = (
            [
                Text.assemble(
                    (element.filter_prompt, self.console.get_style("text")),
                    (element.text, self.console.get_style("text")),
                    "\n",
                )
            ]
            if element.allow_filtering
            else []
        )

        content: list[RenderableType] = []

        content.extend(filter)
        content.append(menu)

        validation_message: tuple[str, ...] = ()

        if message := self.render_validation_message(element):
            validation_message = (message,)

        menu = Group(*content)

        return Group(
            Panel(
                menu,
                title=self.render_input_label(element),
                title_align="left",
                highlight=is_active,
                box=self.box,
            ),
            *validation_message,
        )

    def get_cursor_offset_for_element(self, element: Element) -> CursorOffset:
        from rich_toolkit.input import Input

        top_offset = element.cursor_offset.top
        left_offset = element.cursor_offset.left + 2

        if isinstance(element, Input) and element.inline:
            # we don't support inline inputs yet in border style
            top_offset += 1

        return CursorOffset(top=top_offset, left=left_offset)
