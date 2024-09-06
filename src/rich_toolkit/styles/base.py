from abc import ABC, abstractmethod
from typing import Any, Generator, Iterable, List, Type, TypeVar

from rich.color import Color
from rich.console import (
    Console,
    ConsoleOptions,
    ConsoleRenderable,
    RenderableType,
    RenderResult,
)
from rich.segment import Segment
from rich.text import Text


from rich_toolkit.utils.colors import lighten


ConsoleRenderableClass = TypeVar(
    "ConsoleRenderableClass", bound=Type[ConsoleRenderable]
)


class BaseStyle(ABC):
    result_color: Color

    def __init__(self) -> None:
        self.padding = 2
        self.cursor_offset = 0

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

    def decorate_class(
        self, klass: ConsoleRenderableClass, **metadata: Any
    ) -> ConsoleRenderableClass:
        style = self

        class Decorated(klass):
            def __rich_console__(
                self, console: Console, options: ConsoleOptions
            ) -> RenderResult:
                lines = Segment.split_lines(super().__rich_console__(console, options))  # type: ignore

                yield from style.decorate(lines=lines, console=console, **metadata)

        return Decorated  # type: ignore

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

