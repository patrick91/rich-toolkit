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


def get_terminal_background_color():
    import os
    import re
    import select
    import sys
    import termios
    import tty

    # Only works on Unix-like systems with terminals that support OSC 11
    if not os.isatty(sys.stdin.fileno()):
        return "Terminal not detected"

    # Save terminal settings
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
            return f"Unparseable response: {response}"
        else:
            return "No response from terminal"
    finally:
        # Restore terminal settings
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


def get_terminal_background_color_windows():
    import ctypes
    from ctypes import wintypes

    # Constants from wincon.h
    FOREGROUND_BLUE = 0x0001
    FOREGROUND_GREEN = 0x0002
    FOREGROUND_RED = 0x0004
    FOREGROUND_INTENSITY = 0x0008
    BACKGROUND_BLUE = 0x0010
    BACKGROUND_GREEN = 0x0020
    BACKGROUND_RED = 0x0040
    BACKGROUND_INTENSITY = 0x0080

    # Define the CONSOLE_SCREEN_BUFFER_INFO structure
    class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes._COORD),
            ("dwCursorPosition", wintypes._COORD),
            ("wAttributes", wintypes.WORD),
            ("srWindow", wintypes.SMALL_RECT),
            ("dwMaximumWindowSize", wintypes._COORD),
        ]

    # Get handle to console
    h_console = ctypes.windll.kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE

    # Get console info
    csbi = CONSOLE_SCREEN_BUFFER_INFO()
    if ctypes.windll.kernel32.GetConsoleScreenBufferInfo(h_console, ctypes.byref(csbi)):
        # Extract background color attributes
        bg_color = csbi.wAttributes & 0x00F0

        # Convert to RGB values
        r = 0
        g = 0
        b = 0

        if bg_color & BACKGROUND_RED:
            r = 128
        if bg_color & BACKGROUND_GREEN:
            g = 128
        if bg_color & BACKGROUND_BLUE:
            b = 128
        if bg_color & BACKGROUND_INTENSITY:
            r = min(r + 127, 255)
            g = min(g + 127, 255)
            b = min(b + 127, 255)

        return f"#{r:02x}{g:02x}{b:02x}"
    else:
        return "Failed to get console information"


if __name__ == "__main__":
    try:
        print(get_terminal_background_color())
    except Exception:
        print("trying windows version")
        print(get_terminal_background_color_windows())
