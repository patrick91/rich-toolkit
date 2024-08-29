import string
from typing import Any

import click
from rich._loop import loop_last
from rich.console import Console, ConsoleOptions, Group, RenderableType, RenderResult
from rich.control import Control
from rich.live_render import LiveRender, VerticalOverflowMethod
from rich.segment import Segment
from rich.text import Text

from rich_toolkit.app_style import AppStyle


class LiveRenderWithDecoration(LiveRender):
    def __init__(
        self,
        renderable: RenderableType,
        style: AppStyle,
        vertical_overflow: VerticalOverflowMethod = "ellipsis",
        **metadata: Any,
    ) -> None:
        super().__init__(renderable, vertical_overflow=vertical_overflow)

        self.metadata = metadata
        self.app_style = style

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        renderable = self.renderable
        style = console.get_style(self.style)
        lines = console.render_lines(renderable, options, style=style, pad=False)
        shape = Segment.get_shape(lines)

        _, height = shape
        if height > options.size.height:
            if self.vertical_overflow == "crop":
                lines = lines[: options.size.height]
                shape = Segment.get_shape(lines)
            elif self.vertical_overflow == "ellipsis":
                lines = lines[: (options.size.height - 1)]
                overflow_text = Text(
                    "...",
                    overflow="crop",
                    justify="center",
                    end="",
                    style="live.ellipsis",
                )
                lines.append(list(console.render(overflow_text)))
                shape = Segment.get_shape(lines)
        self._shape = shape

        new_line = Segment.line()

        decorated_lines = Segment.split_lines(
            self.app_style.decorate(lines, **self.metadata)
        )

        for last, line in loop_last(decorated_lines):
            yield from line
            if not last:
                yield new_line

        # for last, (decoration, line) in loop_last(zip(decoration, lines)):
        #     yield from decoration
        #     yield from line
        #     if not last:
        #         yield new_line

    def fix_cursor(self, offset: int) -> Control:
        decoration_lines = list(self.app_style.decorate([[]]))

        decoration = next(Segment.split_lines(decoration_lines))
        decoration_width = Segment.get_line_length(decoration)

        return Control.move_to_column(offset + decoration_width)


class Input:
    def __init__(
        self,
        console: Console,
        title: str,
        style: AppStyle,
        default: str = "",
        **metadata: Any,
    ):
        self.title = title
        self.default = default
        self.text = ""

        self.console = console
        self.style = style

        self._live_render = LiveRenderWithDecoration("", style=self.style, **metadata)
        self._padding_bottom = 1

    def _update_text(self, char: str) -> None:
        if char == "\x7f":
            self.text = self.text[:-1]
        elif char in string.printable:
            self.text += char

    def _render_result(self) -> RenderableType:
        return self.title + " [#aaaaaa]" + (self.text or self.default)

    def _render_input(self) -> Group:
        text = (
            f"[#ffffff]{self.text}[/]" if self.text else f"[#aaaaaa]{self.default}[/]"
        )

        return Group(self.title, text)

    def _refresh(self, show_result: bool = False) -> None:
        renderable = self._render_result() if show_result else self._render_input()

        self._live_render.set_renderable(renderable)

        self._render()

    def _render(self):
        self.console.print(
            self._live_render.position_cursor(),
            self._live_render,
            self._live_render.fix_cursor(len(self.text)),
        )

    def ask(self) -> str:
        self._refresh()

        while True:
            try:
                key = click.getchar()

                if key == "\r":
                    break

                self._update_text(key)

            except KeyboardInterrupt:
                exit()

            self._refresh()

        self._refresh(show_result=True)

        for _ in range(self._padding_bottom):
            self.console.print()

        return self.text or self.default
