from abc import ABC
from typing import Any, Union

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
        self,
        base_color: Union[Color, str],
        title_color: Union[Color, str],
    ) -> None:
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
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.tag_width = kwargs.get("tag_width", 14)

    def _render_tag(self, text: str, background_color: Color) -> RenderDecorationResult:
        style = Style.from_color(Color.parse("#ffffff"), bgcolor=background_color)

        if text:
            text = f" {text} "

        left_padding = self.tag_width - len(text)
        left_padding = max(0, left_padding)

        yield Segment(" " * left_padding)
        yield Segment(text, style=style)
        yield Segment(" " * self.padding)

    def decorate(
        self, lines, animated: bool = False, **kwargs: Any
    ) -> RenderDecorationResult:
        if animated:
            yield from self.decorate_with_animation(lines)

            return

        tag = kwargs.get("tag", "")

        color = self.highlight_color if kwargs.get("title", False) else self.base_color

        for index, line in enumerate(lines):
            text = tag if index == 0 else ""
            yield from self._render_tag(text, background_color=color)
            yield from line
            yield Segment.line()

    def decorate_with_animation(self, lines) -> RenderDecorationResult:
        block = "█"

        block_length = 5

        colors = [lighten(self.base_color, 0.1 * i) for i in range(0, block_length)]

        left_padding = self.tag_width - block_length
        left_padding = max(0, left_padding)

        self._animation_counter += 1

        for index, line in enumerate(lines):
            if index == 0:
                yield Segment(" " * left_padding)

                for j in range(block_length):
                    color_index = (j + self._animation_counter) % len(colors)
                    yield Segment(block, style=Style(color=colors[color_index]))

                yield Segment(" " * self.padding)
            else:
                yield Segment(" " * self.tag_width)

            yield from line
            yield Segment.line()


class FancyAppStyle(AppStyle):
    def decorate(
        self, lines, animated: bool = False, **kwargs: Any
    ) -> RenderDecorationResult:
        if animated:
            colors = [lighten(self.base_color, 0.1 * i) for i in range(0, 5)]

            self._animation_counter += 1

            color_index = self._animation_counter % len(colors)

            for index, (last, line) in enumerate(loop_last(lines)):
                if index == 0:
                    yield Segment("◆ ", style=Style(color=colors[color_index]))
                else:
                    yield Segment("  ")
                yield from line
                yield Segment.line()

            return

        for index, (last, line) in enumerate(loop_last(lines)):
            if index == 0:
                decoration = "┌ " if kwargs.get("title", False) else "◆ "
            elif last:
                decoration = "└ "
            else:
                decoration = "│ "

            yield Segment(decoration)
            yield from line
            yield Segment.line()

    def render_empty_line(self) -> Text:
        return Text("│")
