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


def lighten_text(text: Text, base_color: Color, amount: float) -> Text:
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
            style._color = lighten(style.color, amount)

        new_spans.append(span._replace(style=style))
    text._spans = new_spans
    text.style = Style(color=lighten(base_color, amount))
    return text


if __name__ == "__main__":
    from rich import print

    print(lighten(Color.from_rgb(0, 0, 0), 0.5))

    for i in range(10):
        print(
            lighten_text(
                Text.from_markup("[red]Hello[/red], World!"),
                Color.from_rgb(0, 0, 0),
                i / 10,
            )
        )
