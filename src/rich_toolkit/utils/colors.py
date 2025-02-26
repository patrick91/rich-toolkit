from typing import Callable

from rich.color import Color
from rich.color_triplet import ColorTriplet
from rich.style import Style
from rich.text import Text


def lighten(color: Color, amount: float) -> Color:
    triplet = color.triplet

    if not triplet:
        triplet = color.get_truecolor()

    r, g, b = triplet

    r = int(r + (255 - r) * amount)
    g = int(g + (255 - g) * amount)
    b = int(b + (255 - b) * amount)

    return Color.from_triplet(ColorTriplet(r, g, b))


def darken(color: Color, amount: float) -> Color:
    triplet = color.triplet

    if not triplet:
        triplet = color.get_truecolor()

    r, g, b = triplet

    r = int(r * (1 - amount))
    g = int(g * (1 - amount))
    b = int(b * (1 - amount))

    return Color.from_triplet(ColorTriplet(r, g, b))


def _brighten_text(
    text: Text, base_color: Color, amount: float, func: Callable[[Color, float], Color]
) -> Text:
    """
    Lighten the text by the given amount.

    It will ignore any background colors.

    Args:
        text (Text): The text to lighten.
        amount (float): The amount to lighten the text by.

    Returns:
        Text: The text with the new color.
    """
    new_spans = []
    for span in text._spans:
        style: Style | str = span.style

        if isinstance(style, str):
            style = Style.parse(style)

        if style.color:
            color = style.color

            if color == Color.default():
                color = base_color

            style = style.copy()
            style._color = func(color, amount)

        new_spans.append(span._replace(style=style))
    text = text.copy()
    text._spans = new_spans
    text.style = Style(color=func(base_color, amount))
    return text


def lighten_text(text: Text, base_color: Color, amount: float) -> Text:
    return _brighten_text(text, base_color, amount, lighten)


def darken_text(text: Text, base_color: Color, amount: float) -> Text:
    return _brighten_text(text, base_color, amount, darken)


if __name__ == "__main__":
    from rich import print

    print("######## lighten ##########")

    for i in range(1, 10):
        print(
            lighten_text(
                Text.from_ansi(
                    f"\033[4;39mHello\033[0m, World! \033[4;39mHello\033[0m {i / 10}"
                ),
                Color.from_rgb(0, 0, 0),
                i / 10,
            )
        )

    print("######## darken ##########")

    for i in range(10):
        print(
            darken_text(
                Text.from_ansi(
                    f"\033[4;39mHello\033[0m, World! \033[4;39mHello\033[0m {i / 10}"
                ),
                Color.from_rgb(255, 255, 255),
                i / 10,
            )
        )
