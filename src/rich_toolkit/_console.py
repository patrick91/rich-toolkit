"""Encoding-safe human output without changing the application's streams."""

from __future__ import annotations

from copy import copy
from functools import lru_cache
from typing import Any, Iterable, Optional
from urllib.parse import quote

from rich.align import Align
from rich.console import Console, ConsoleOptions, Group, RenderableType
from rich.constrain import Constrain
from rich.measure import Measurement
from rich.padding import Padding
from rich.panel import Panel
from rich.protocol import rich_cast
from rich.segment import Segment
from rich.style import Style
from rich.table import Table
from rich.text import Text


def display_text(value: str, encoding: str) -> str:
    """Preserve supported characters and replace unencodable ones with '?'."""
    return value.encode(encoding, errors="replace").decode(encoding)


def prepare_text(value: Text, encoding: str) -> Text:
    """Replace unsupported characters in a display copy, preserving styles."""
    displayed = display_text(value.plain, encoding)
    if displayed == value.plain:
        return value

    result = value.copy()
    result.plain = displayed
    return result


def _prepare_renderable(renderable: RenderableType, encoding: str) -> RenderableType:
    """Prepare copies of Rich containers before they measure their children."""
    renderable = rich_cast(renderable)
    if isinstance(renderable, Text):
        return prepare_text(renderable, encoding)
    if isinstance(renderable, Table):
        table = copy(renderable)
        table.columns = [copy(column) for column in renderable.columns]
        for column in table.columns:
            column.header = _prepare_renderable(column.header, encoding)
            column.footer = _prepare_renderable(column.footer, encoding)
            # Rich's measurement reads the cells directly, bypassing Console.render.
            column._cells = [
                _prepare_renderable(cell, encoding) for cell in column.cells
            ]
        return table
    if isinstance(renderable, Group):
        group = copy(renderable)
        group._render = [
            _prepare_renderable(child, encoding) for child in renderable.renderables
        ]
        return group
    if isinstance(renderable, (Align, Constrain, Padding, Panel)):
        wrapper = copy(renderable)
        wrapper.renderable = _prepare_renderable(renderable.renderable, encoding)
        if isinstance(wrapper, Panel):
            for attribute in ("title", "subtitle"):
                title = getattr(wrapper, attribute)
                if title is not None:
                    text = Text.from_markup(title) if isinstance(title, str) else title
                    setattr(wrapper, attribute, prepare_text(text, encoding))
        return wrapper
    return renderable


@lru_cache(maxsize=128)
def _prepare_style(style: Style, encoding: str) -> Style:
    if style.link:
        try:
            style.link.encode(encoding)
        except UnicodeEncodeError:
            # Preserve URL delimiters and existing escapes; encode Unicode as UTF-8.
            return style.update_link(quote(style.link, safe=":/?#[]@!$&'()*+,;=%"))
    return style


class ToolkitConsole(Console):
    def render_str(self, text: str, **kwargs: Any) -> Text:
        return prepare_text(super().render_str(text, **kwargs), self.encoding)

    def measure(
        self, renderable: RenderableType, *, options: Optional[ConsoleOptions] = None
    ) -> Measurement:
        return super().measure(
            _prepare_renderable(renderable, self.encoding), options=options
        )

    def render(
        self, renderable: RenderableType, options: Optional[ConsoleOptions] = None
    ) -> Iterable[Segment]:
        renderable = _prepare_renderable(renderable, self.encoding)

        for segment in super().render(renderable, options):
            # Custom renderables may emit segments directly, bypassing Text.
            # Never transform terminal control sequences.
            if segment.control:
                yield segment
            else:
                style = segment.style
                if style is not None and style.link:
                    style = _prepare_style(style, self.encoding)
                yield Segment(display_text(segment.text, self.encoding), style)
