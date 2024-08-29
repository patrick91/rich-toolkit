from abc import ABC, abstractmethod
from typing import Any, Callable, Generator, Union

from rich.color import Color
from rich.segment import Segment
from rich.style import Style

RenderDecorationResult = Generator[Segment, None, None]
RenderDecoration = Callable[..., RenderDecorationResult]


class Decoration(ABC):
    @abstractmethod
    def for_title(self, **kwargs: Any) -> RenderDecorationResult:
        raise NotImplementedError()

    @abstractmethod
    def render(self, **kwargs) -> RenderDecorationResult:
        raise NotImplementedError()


class TagDecoration(Decoration):
    def __init__(
        self,
        base_color: Union[Color, str],
        title_color: Union[Color, str],
        tag_width: int = 14,
    ) -> None:
        self.tag_width = tag_width
        self.padding = 2

        self.base_color = (
            Color.parse(base_color) if isinstance(base_color, str) else base_color
        )
        self.title_color = (
            Color.parse(title_color) if isinstance(title_color, str) else title_color
        )

    def _render_tag(self, text: str, background_color: Color) -> RenderDecorationResult:
        title_style = Style.from_color(Color.parse("#ffffff"), bgcolor=background_color)

        if text:
            text = f" {text} "

        left_padding = self.tag_width - len(text)
        left_padding = max(0, left_padding)

        yield Segment(" " * left_padding)
        yield Segment(text, style=title_style)
        yield Segment(" " * self.padding)

    def for_title(self, **kwargs: Any) -> RenderDecorationResult:
        yield from self._render_tag(
            kwargs.get("tag", ""), background_color=self.title_color
        )

    def render(self, **kwargs) -> RenderDecorationResult:
        tag = kwargs.get("tag", "")

        yield from self._render_tag(tag, background_color=self.base_color)

        while True:
            yield Segment.line()
            yield from self._render_tag("", background_color=self.base_color)


class FancyDecoration(Decoration):
    def for_title(self, **kwargs: Any) -> RenderDecorationResult:
        yield Segment("┌ ")

    def render(self, **kwargs) -> RenderDecorationResult:
        yield Segment("◆")
        yield Segment(" ")
        yield Segment.line()
        # yield Segment("│")
        yield Segment("└")
        yield Segment(" ")
