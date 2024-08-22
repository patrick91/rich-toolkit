from rich.color import Color
from rich.color_triplet import ColorTriplet
from rich.console import Console, Group, RenderableType
from rich.live import Live
from rich.style import Style
from rich.text import Text

from .row import SplitRow


def lighten(color: Color, amount: float) -> Color:
    assert color.triplet

    r, g, b = color.triplet

    r = int(r + (255 - r) * amount)
    g = int(g + (255 - g) * amount)
    b = int(b + (255 - b) * amount)

    return Color.from_triplet(ColorTriplet(r, g, b))


class Progress(Live):
    def __init__(
        self,
        title: str,
        console: Console | None = None,
        base_color: Color = Color.parse("#079587"),
    ) -> None:
        self.counter = 0
        self.current_message = title
        self.block_length = 5
        self.base_color = base_color

        self.colors = [
            self.base_color,
            lighten(self.base_color, 0.1),
            lighten(self.base_color, 0.2),
            lighten(self.base_color, 0.3),
            lighten(self.base_color, 0.4),
            lighten(self.base_color, 0.5),
        ]

        super().__init__(console=console, refresh_per_second=8)

    # TODO: remove this once rich uses "Self"
    def __enter__(self) -> "Progress":
        self.start(refresh=self._renderable is not None)
        return self

    def _get_animation(self) -> RenderableType:
        block = "█"

        text = Text(end="")

        if not self._started:
            text = Text(
                block * self.block_length, end="", style=Style(color=self.colors[0])
            )
        else:
            for j in range(self.block_length):
                color_index = (j + self.counter) % len(self.colors)
                text.append(block, style=Style(color=self.colors[color_index]))

            self.counter += 1

        return text

    def get_renderable(self) -> RenderableType:
        return Group(SplitRow(self._get_animation(), self.current_message), "")

    def log(self, text: str) -> None:
        self.current_message = text

    def set_error(self, text: str) -> None:
        self.current_message = text
        self.colors = [Color.parse("red")]
