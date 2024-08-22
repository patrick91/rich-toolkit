from rich.color import Color
from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.segment import Segment
from rich.style import Style
from typing_extensions import Literal


class SplitRow:
    def __init__(self, left: RenderableType, right: RenderableType):
        self.left = left
        self.right = right
        self.left_width = 10
        self.padding = 1

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        table_style = console.get_style("none")

        left_padding = self.left_width - len(self.left)
        left_padding = max(0, left_padding)

        right_width = options.max_width - self.left_width - (2 * self.padding)

        right_options = options.update(width=right_width)
        right_lines = console.render_lines(self.right, right_options)

        padding = Segment(" " * self.padding, style=table_style)

        for first, line in enumerate(right_lines):
            if first == 0:
                yield Segment(" " * left_padding)
                yield self.left
                yield padding
            else:
                yield Segment(" " * (self.left_width + 1), style=table_style)
            yield padding
            yield from line
            yield Segment.line()


class RowWithTitle:
    def __init__(
        self,
        title: str,
        content: RenderableType,
        style: Literal["error", "default"] = "default",
        base_color: Color = Color.parse("#f7393d"),
    ):
        white = Color.parse("#ffffff")

        self.title = title
        self.content = content
        self.left_width = 10
        self.padding = 1
        self.title_style = (
            Style.from_color(white, bgcolor=base_color)
            if style == "default"
            else Style.parse("bold #ffffff on #FF6C8D")
        )

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        table_style = console.get_style("none")

        title_text = f" {self.title} "
        left_padding = self.left_width - len(title_text)
        left_padding = max(0, left_padding)

        right_width = options.max_width - self.left_width - (2 * self.padding)

        right_options = options.update(width=right_width)
        right_lines = console.render_lines(self.content, right_options)

        padding = Segment(" " * self.padding, style=table_style)

        for first, line in enumerate(right_lines):
            if first == 0:
                yield Segment(" " * left_padding)
                yield Segment(title_text, style=self.title_style)
                yield padding
            else:
                yield Segment(" " * (self.left_width + 1), style=table_style)
            yield padding
            yield from line
            yield Segment.line()
