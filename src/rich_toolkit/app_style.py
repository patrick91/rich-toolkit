from abc import ABC, abstractmethod
from typing import Any, Generator, Iterable, List, Union

from rich._loop import loop_first_last
from rich.color import Color
from rich.console import (
    Console,
    ConsoleOptions,
    ConsoleRenderable,
    RenderableType,
    RenderResult,
)
from rich.segment import Segment
from rich.style import Style
from rich.text import Text

from .utils.colors import lighten


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

    def empty_line(self) -> Text:
        return Text(" ")

    def with_decoration(
        self, content: RenderableType, animated: bool = False, **metadata: Any
    ) -> ConsoleRenderable:
        class WithDecoration:
            @staticmethod
            def __rich_console__(
                console: Console, options: ConsoleOptions
            ) -> RenderResult:
                lines = console.render_lines(content, options, pad=False)

                for line in Segment.split_lines(
                    self.decorate(lines, animated=animated, **metadata)
                ):
                    yield from line
                    yield Segment.line()

        return WithDecoration()

    @abstractmethod
    def decorate(
        self, lines: Iterable[List[Segment]], animated: bool = False, **kwargs: Any
    ) -> Generator[Segment, None, None]:
        raise NotImplementedError()


class TaggedAppStyle(AppStyle):
    def __init__(self, *args, **kwargs) -> None:
        self.tag_width = kwargs.pop("tag_width", 14)

        super().__init__(*args, **kwargs)

    def _render_tag(
        self, text: str, background_color: Color
    ) -> Generator[Segment, None, None]:
        style = Style.from_color(Color.parse("#ffffff"), bgcolor=background_color)

        if text:
            text = f" {text} "

        left_padding = self.tag_width - len(text)
        left_padding = max(0, left_padding)

        yield Segment(" " * left_padding)
        yield Segment(text, style=style)
        yield Segment(" " * self.padding)

    def decorate(
        self, lines: Iterable[List[Segment]], animated: bool = False, **kwargs: Any
    ) -> Generator[Segment, None, None]:
        if animated:
            yield from self.decorate_with_animation(lines)

            return

        tag = kwargs.get("tag", "")

        color = self.highlight_color if kwargs.get("title", False) else self.base_color

        for first, last, line in loop_first_last(lines):
            text = tag if first else ""
            yield from self._render_tag(text, background_color=color)
            yield from line

            if not last:
                yield Segment.line()

    def decorate_with_animation(
        self, lines: Iterable[List[Segment]]
    ) -> Generator[Segment, None, None]:
        block = "█"

        block_length = 5

        colors = [lighten(self.base_color, 0.1 * i) for i in range(0, block_length)]

        left_padding = self.tag_width - block_length
        left_padding = max(0, left_padding)

        self._animation_counter += 1

        for first, last, line in loop_first_last(lines):
            if first:
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
        self, lines: Iterable[List[Segment]], animated: bool = False, **kwargs: Any
    ) -> Generator[Segment, None, None]:
        if animated:
            colors = [lighten(self.base_color, 0.1 * i) for i in range(0, 5)]

            self._animation_counter += 1

            color_index = self._animation_counter % len(colors)

            for first, last, line in loop_first_last(lines):
                if first:
                    yield Segment("◆ ", style=Style(color=colors[color_index]))
                else:
                    yield Segment("  ")
                yield from line
                yield Segment.line()

            return

        for first, last, line in loop_first_last(lines):
            if first:
                decoration = "┌ " if kwargs.get("title", False) else "◆ "
            elif last:
                decoration = "└ "
            else:
                decoration = "│ "

            yield Segment(decoration)
            yield from line

            if not last:
                yield Segment.line()

    def empty_line(self) -> Text:
        return Text("│")
