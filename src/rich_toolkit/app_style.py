from abc import ABC
from typing import Any

from rich._loop import loop_last
from rich.color import Color
from rich.color_triplet import ColorTriplet
from rich.segment import Segment
from rich.style import Style
from rich.text import Text

from rich_toolkit.decorations import RenderDecorationResult


class AppStyle(ABC):
    base_color: Color
    highlight_color: Color
    text_color: Color
    result_color: Color

    def __init__(
        self, base_color: Color | str, title_color: Color | str, tag_width: int = 14
    ) -> None:
        self.tag_width = tag_width
        self.padding = 2

        self.text_color = Color.parse("#ffffff")
        self.result_color = Color.parse("#aaaaaa")
        self.base_color = (
            Color.parse(base_color) if isinstance(base_color, str) else base_color
        )
        self.highlight_color = (
            Color.parse(title_color) if isinstance(title_color, str) else title_color
        )

        self._animation_counter = 0

    def render_empty_line(self) -> Text:
        return Text(" ")


def lighten(color: Color, amount: float) -> Color:
    assert color.triplet

    r, g, b = color.triplet

    r = int(r + (255 - r) * amount)
    g = int(g + (255 - g) * amount)
    b = int(b + (255 - b) * amount)

    return Color.from_triplet(ColorTriplet(r, g, b))


class TaggedAppStyle(AppStyle):
    def _render_tag(self, text: str, background_color: Color) -> RenderDecorationResult:
        style = Style.from_color(Color.parse("#ffffff"), bgcolor=background_color)

        if text:
            text = f" {text} "

        left_padding = self.tag_width - len(text)
        left_padding = max(0, left_padding)

        yield Segment(" " * left_padding)
        yield Segment(text, style=style)
        yield Segment(" " * self.padding)

    def render_decoration(
        self, animated: bool = False, **kwargs: Any
    ) -> RenderDecorationResult:
        if animated:
            yield from self.render_animated_decoration(**kwargs)
            return

        tag = kwargs.get("tag", "")

        color = self.highlight_color if kwargs.get("title", False) else self.base_color

        yield from self._render_tag(tag, background_color=color)

        while True:
            yield Segment.line()
            yield from self._render_tag("", background_color=color)

    def render_animated_decoration(self, **kwargs) -> RenderDecorationResult:
        block = "█"

        block_length = 5

        colors = [lighten(self.base_color, 0.1 * i) for i in range(0, block_length)]

        left_padding = self.tag_width - block_length
        left_padding = max(0, left_padding)

        self._animation_counter += 1

        yield Segment(" " * left_padding)

        for j in range(block_length):
            color_index = (j + self._animation_counter) % len(colors)
            yield Segment(block, style=Style(color=colors[color_index]))

        yield Segment(" " * self.padding)
        yield Segment.line()


class FancyAppStyle(AppStyle):
    def decorate(
        self, lines, animated: bool = False, **kwargs: Any
    ) -> RenderDecorationResult:
        for index, (last, line) in enumerate(loop_last(lines)):
            if index == 0:
                decoration = "┌ " if kwargs.get("title", False) else "◆"
            elif last:
                decoration = "└ "
            else:
                decoration = "│ "

            yield Segment(decoration)
            yield from line
            yield Segment.line()

    def render_animated_decoration(self, **kwargs) -> RenderDecorationResult:
        colors = [lighten(self.base_color, 0.1 * i) for i in range(0, 5)]

        self._animation_counter += 1

        color_index = self._animation_counter % len(colors)

        yield Segment("◆", style=Style(color=colors[color_index]))

        yield Segment(" ")
        yield Segment.line()

    def render_empty_line(self) -> Text:
        return Text("│")
