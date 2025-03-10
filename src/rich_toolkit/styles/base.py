from typing import Type, TypeVar

from rich.color import Color
from rich.console import (
    ConsoleRenderable,
    RenderableType,
)
from rich.text import Text

from rich_toolkit.utils.colors import lighten_text

ConsoleRenderableClass = TypeVar(
    "ConsoleRenderableClass", bound=Type[ConsoleRenderable]
)


class BaseStyle:
    # TODO: make this an ABC?

    def empty_line(self) -> RenderableType:
        return ""

    def render_progress_log_line(
        self, line: str | Text, index: int, max_lines: int = -1, total_lines: int = -1
    ) -> Text:
        line = Text.from_markup(line) if isinstance(line, str) else line
        if max_lines == -1:
            return line

        # Adjust minimum brightness based on number of lines
        # Fewer lines = higher minimum brightness
        min_brightness = max(0.4, 1.0 - (total_lines / max_lines) * 0.6)
        brightness_range = 1.0 - min_brightness

        # Calculate brightness based on position in the sequence
        brightness_pct = (index / total_lines) * brightness_range + min_brightness

        # Apply brightness to RGB values
        r = g = b = int(255 * brightness_pct)

        color = f"#{r:02x}{g:02x}{b:02x}"

        return lighten_text(line, Color.parse(color), brightness_pct)
