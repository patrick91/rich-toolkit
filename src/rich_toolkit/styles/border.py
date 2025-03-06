from typing import Any

from rich import box
from rich.console import Group, RenderableType
from rich.text import Text

from rich_toolkit._render_wrapper import RenderWrapper
from rich_toolkit.element import CursorOffset, Element
from rich_toolkit.input import Input
from rich_toolkit.panel import Panel
from rich_toolkit.streaming_container import StreamingContainer

from .base import BaseStyle


class BorderedStyle(BaseStyle):
    def decorate(
        self,
        renderable: Element,
        is_active: bool = False,
        **metadata: Any,
    ) -> RenderableType:
        if isinstance(renderable, StreamingContainer):
            return RenderWrapper(
                Group(
                    Panel.fit(Group(*renderable.logs), title="LOL", title_align="left"),
                    renderable.footer_content,
                ),
                CursorOffset(top=0, left=0),
            )

        if isinstance(renderable, Input):
            # TODO: can we use some of the existing render code from input? (maybe just for inline?)
            # or we can remove the label from the input so we don't render it twice?

            if renderable.inline:
                content = f"─ {renderable.label}: {renderable.text} ─"

                cursor_left = len(renderable.label) + 4 + renderable.cursor_left
                cursor_top = 1

                return RenderWrapper(
                    content,
                    CursorOffset(top=cursor_top, left=cursor_left),
                )
            else:
                if renderable.input.valid is False:
                    validation_message = (
                        Text("This field is required", style="bold red"),
                    )
                else:
                    validation_message = ()

                content = Group(
                    Panel(
                        renderable.text,
                        highlight=is_active,
                        title=renderable.label,
                        title_align="left",
                        width=50,
                        box=box.SQUARE,
                    ),
                    *validation_message,
                )

                cursor_left = renderable.cursor_left + 2
                cursor_top = 2

                return RenderWrapper(
                    content,
                    CursorOffset(top=cursor_top, left=cursor_left),
                )

        return RenderWrapper(
            renderable.render(is_active=is_active),
            CursorOffset(top=0, left=0),
        )
