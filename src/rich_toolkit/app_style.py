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
    result_color: Color

    def __init__(self) -> None:
        self.padding = 2

        self._animation_counter = 0

    def empty_line(self) -> Text:
        return Text(" ")

    def with_decoration(
        self, *renderables: RenderableType, animated: bool = False, **metadata: Any
    ) -> ConsoleRenderable:
        class WithDecoration:
            @staticmethod
            def __rich_console__(
                console: Console, options: ConsoleOptions
            ) -> RenderResult:
                for content in renderables:
                    lines = console.render_lines(content, options, pad=False)

                    for line in Segment.split_lines(
                        self.decorate(
                            lines=lines, console=console, animated=animated, **metadata
                        )
                    ):
                        yield from line
                        yield Segment.line()

        return WithDecoration()

    @abstractmethod
    def decorate(
        self,
        console: Console,
        lines: Iterable[List[Segment]],
        animated: bool = False,
        **kwargs: Any,
    ) -> Generator[Segment, None, None]:
        raise NotImplementedError()

    def _get_animation_colors(self, console: Console, steps: int = 5) -> List[Color]:
        base_color = console.get_style("progress").bgcolor

        # to lighten the colors we need to convert them to RGB
        # if we are using a named colors we can't do that unfortunately
        if base_color and base_color.triplet is None:
            base_color = None

        return (
            [lighten(base_color, 0.1 * i) for i in range(0, steps)]
            if base_color
            else [Color.parse("black")]
        )


class TaggedAppStyle(AppStyle):
    def __init__(self, *args, **kwargs) -> None:
        self.tag_width = kwargs.pop("tag_width", 14)

        super().__init__(*args, **kwargs)

    def _render_tag(
        self,
        text: str,
        console: Console,
        **metadata: Any,
    ) -> Generator[Segment, None, None]:
        style_name = "tag.title" if metadata.get("title", False) else "tag"

        style = console.get_style(style_name)

        if text:
            text = f" {text} "

        left_padding = self.tag_width - len(text)
        left_padding = max(0, left_padding)

        yield Segment(" " * left_padding)
        yield Segment(text, style=style)
        yield Segment(" " * self.padding)

    def decorate(
        self,
        console: Console,
        lines: Iterable[List[Segment]],
        animated: bool = False,
        **metadata: Any,
    ) -> Generator[Segment, None, None]:
        if animated:
            yield from self.decorate_with_animation(lines=lines, console=console)

            return

        tag = metadata.get("tag", "")

        for first, last, line in loop_first_last(lines):
            text = tag if first else ""
            yield from self._render_tag(text, console=console, **metadata)
            yield from line

            if not last:
                yield Segment.line()

    def decorate_with_animation(
        self, console: Console, lines: Iterable[List[Segment]]
    ) -> Generator[Segment, None, None]:
        block = "█"
        block_length = 5
        colors = self._get_animation_colors(console, steps=block_length)

        left_padding = self.tag_width - block_length
        left_padding = max(0, left_padding)

        self._animation_counter += 1

        for first, _, line in loop_first_last(lines):
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
        self,
        console: Console,
        lines: Iterable[List[Segment]],
        animated: bool = False,
        **kwargs: Any,
    ) -> Generator[Segment, None, None]:
        if animated:
            colors = self._get_animation_colors(console)

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
