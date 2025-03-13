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
    Lighten the text by the given amount and function.

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


def get_terminal_background_color(default_color: str = "#000000") -> str:
    import os
    import re
    import select
    import sys

    try:
        import termios
        import tty
    except ImportError:
        # Not on Unix-like systems (probably Windows), so we return the default color
        return default_color

    if not os.isatty(sys.stdin.fileno()):
        return default_color

    # Save terminal settings so we can restore them
    old_settings = termios.tcgetattr(sys.stdin)

    try:
        # Set terminal to raw mode
        tty.setraw(sys.stdin)

        # Send OSC 11 escape sequence to query background color
        sys.stdout.write("\033]11;?\033\\")
        sys.stdout.flush()

        # Wait for response with timeout
        if select.select([sys.stdin], [], [], 1.0)[0]:
            # Read response
            response = ""
            while True:
                char = sys.stdin.read(1)
                response += char

                if char == "\\":  # End of OSC response
                    break
                if len(response) > 50:  # Safety limit
                    break

            # Parse the response (format: \033]11;rgb:RRRR/GGGG/BBBB\033\\)
            match = re.search(
                r"rgb:([0-9a-f]+)/([0-9a-f]+)/([0-9a-f]+)", response, re.IGNORECASE
            )
            if match:
                r, g, b = match.groups()
                # Convert to standard hex format
                r = int(r[0:2], 16)
                g = int(g[0:2], 16)
                b = int(b[0:2], 16)
                return f"#{r:02x}{g:02x}{b:02x}"

            return default_color
        else:
            return default_color
    finally:
        # Restore terminal settings
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


if __name__ == "__main__":
    print(get_terminal_background_color())
