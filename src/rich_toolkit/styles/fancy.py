from typing import Any, Generator, Iterable, List

from rich._loop import loop_first_last
from rich.console import (
    Console,
)
from rich.segment import Segment
from rich.style import Style
from rich.text import Text


from .base import BaseStyle


class FancyStyle(BaseStyle):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.cursor_offset = 2

    def decorate(
        self,
        console: Console,
        lines: Iterable[List[Segment]],
        animated: bool = False,
        **metadata: Any,
    ) -> Generator[Segment, None, None]:
        if animated:
            colors = self._get_animation_colors(console, **metadata)

            self._animation_counter += 1

            color_index = self._animation_counter % len(colors)

            for first, last, line in loop_first_last(lines):
                if first:
                    yield Segment("◆ ", style=Style(color=colors[color_index]))
                else:
                    yield Segment("│ ")
                yield from line
                yield Segment.line()

            return

        for first, last, line in loop_first_last(lines):
            if first:
                decoration = "┌ " if metadata.get("title", False) else "◆ "
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
