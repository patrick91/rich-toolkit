from abc import ABC, abstractmethod
from typing import Any, Type, TypeVar

from rich.color import Color
from rich.console import (
    ConsoleRenderable,
    RenderableType,
)
from rich.style import Style
from rich.text import Text

from rich_toolkit.element import CursorOffset, Element
from rich_toolkit.utils.colors import fade_text, get_terminal_background_color

ConsoleRenderableClass = TypeVar(
    "ConsoleRenderableClass", bound=Type[ConsoleRenderable]
)


class BaseStyle(ABC):
    def __init__(self, background_color: str = "#000000"):
        self.background_color = get_terminal_background_color(background_color)

    def empty_line(self) -> RenderableType:
        return ""

    def render_progress_log_line(
        self,
        line: str | Text,
        index: int,
        max_lines: int = -1,
        total_lines: int = -1,
    ) -> Text:
        line = Text.from_markup(line) if isinstance(line, str) else line
        if max_lines == -1:
            return line

        shown_lines = min(total_lines, max_lines)

        # this is the minimum brightness based on the max_lines
        min_brightness = 0.4
        # but we want to have a slightly higher brightness if there's less than max_lines
        # otherwise you could get the something like this:

        # line 1 -> very dark
        # line 2 -> slightly darker
        # line 3 -> normal

        # which is ok, but not great, so we we increase the brightness if there's less than max_lines
        # so that the last line is always the brightest
        current_min_brightness = min_brightness + abs(shown_lines - max_lines) * 0.1
        current_min_brightness = min(max(current_min_brightness, min_brightness), 1.0)

        brightness_multiplier = ((index + 1) / shown_lines) * (
            1.0 - current_min_brightness
        ) + current_min_brightness

        text = Text(
            str(brightness_multiplier),
            style=Style(
                color=Color.from_rgb(
                    255 * brightness_multiplier,
                    255 * brightness_multiplier,
                    255 * brightness_multiplier,
                )
            ),
        )

        return fade_text(
            line,
            text_color=Color.from_rgb(255, 255, 255),
            background_color=self.background_color,
            brightness_multiplier=brightness_multiplier,
        )

    @abstractmethod
    def decorate(
        self,
        renderable: Element | str,
        is_active: bool = False,
        done: bool = False,
        parent: Element | None = None,
        **metadata: Any,
    ) -> RenderableType:
        pass

    def get_cursor_offset_for_element(self, element: Element) -> CursorOffset:
        return CursorOffset(top=0, left=0)
