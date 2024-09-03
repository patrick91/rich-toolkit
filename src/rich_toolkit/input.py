import string
from typing import Any

import click
from rich.console import Console, ConsoleOptions, Group, RenderableType, RenderResult
from rich.control import Control
from rich.live_render import LiveRender, VerticalOverflowMethod
from rich.segment import Segment

from rich_toolkit.app_style import AppStyle


class LiveRenderWithDecoration(LiveRender):
    def __init__(
        self,
        renderable: RenderableType,
        style: AppStyle,
        console: Console,
        vertical_overflow: VerticalOverflowMethod = "ellipsis",
        **metadata: Any,
    ) -> None:
        super().__init__(renderable, vertical_overflow=vertical_overflow)

        self.metadata = metadata
        self.app_style = style
        self.console = console

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        lines = Segment.split_lines(super().__rich_console__(console, options))  # type: ignore

        yield from self.app_style.decorate(
            lines=lines, console=console, **self.metadata
        )

    def fix_cursor(self, offset: int) -> Control:
        # TODO: do we need the actual console here?
        decoration_lines = list(
            self.app_style.decorate(lines=[[]], console=self.console)
        )

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

        self._live_render = LiveRenderWithDecoration(
            "", console=console, style=self.style, **metadata
        )
        self._padding_bottom = 1

    def _update_text(self, char: str) -> None:
        if char == "\x7f":
            self.text = self.text[:-1]
        elif char in string.printable:
            self.text += char

    def _render_result(self) -> RenderableType:
        return self.title + " [result]" + (self.text or self.default)

    def _render_input(self) -> Group:
        text = (
            f"[text]{self.text}[/]" if self.text else f"[placeholder]{self.default}[/]"
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
