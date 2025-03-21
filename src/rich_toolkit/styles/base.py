from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Type, TypeVar, Union, Optional, Dict
from typing_extensions import Literal

from rich.color import Color
from rich.console import ConsoleRenderable, RenderableType
from rich.theme import Theme
from rich.text import Text
from rich.console import Console
from rich_toolkit.element import CursorOffset, Element
from rich_toolkit.utils.colors import (
    lighten,
    fade_text,
    get_terminal_background_color,
    get_terminal_text_color,
)

ConsoleRenderableClass = TypeVar(
    "ConsoleRenderableClass", bound=Type[ConsoleRenderable]
)


class BaseStyle(ABC):
    brightness_multiplier = 0.1

    base_theme = {
        "tag.title": "bold",
        "tag": "bold",
        "text": "#ffffff",
        "selected": "green",
        "result": "white",
        "progress": "on #893AE3",
        "error": "red",
        "cancelled": "red",
        # is there a way to make nested styles?
        # like label.active uses active style if not set?
        "active": "green",
        "title.error": "white",
        "title.cancelled": "white",
        "placeholder": "grey62",
        "placeholder.cancelled": "grey62 strike",
    }

    def __init__(
        self,
        theme: Optional[Dict[str, str]] = None,
        background_color: str = "#000000",
        text_color: str = "#FFFFFF",
    ):
        self.background_color = get_terminal_background_color(background_color)
        self.text_color = get_terminal_text_color(text_color)
        self.animation_counter = 0

        base_theme = Theme(self.base_theme)
        self.console = Console(theme=base_theme)

        if theme:
            self.console.push_theme(Theme(theme))

    def empty_line(self) -> RenderableType:
        return " "

    def _get_animation_colors(
        self,
        steps: int = 5,
        breathe: bool = False,
        animation_status: Literal["started", "stopped", "error"] = "started",
        **metadata: Any,
    ) -> list[Color]:
        animated = animation_status == "started"

        if animation_status == "error":
            base_color = self.console.get_style("error").color

            if base_color is None:
                base_color = Color.parse("red")

        else:
            base_color = self.console.get_style("progress").bgcolor

        if not base_color:
            base_color = Color.from_rgb(255, 255, 255)

        if breathe:
            steps = steps // 2

        if animated and base_color.triplet is not None:
            colors = [
                lighten(base_color, self.brightness_multiplier * i)
                for i in range(0, steps)
            ]

        else:
            colors = [base_color] * steps

        if breathe:
            colors = colors + colors[::-1]

        return colors

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

        return fade_text(
            line,
            text_color=Color.parse(self.text_color),
            background_color=self.background_color,
            brightness_multiplier=brightness_multiplier,
        )

    @abstractmethod
    def decorate(
        self,
        renderable: Union[Element, str],
        is_active: bool = False,
        done: bool = False,
        parent: Optional[Element] = None,
        **metadata: Any,
    ) -> RenderableType:
        pass

    def get_cursor_offset_for_element(self, element: Element) -> CursorOffset:
        return element.cursor_offset
