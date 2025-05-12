import random

import rich

from rich_toolkit import RichToolkit, RichToolkitTheme
from rich_toolkit.styles import FancyStyle, TaggedStyle


def random_name_generator() -> str:
    return f"{random.choice(['fancy', 'cool', 'awesome'])}-{random.choice(['banana', 'apple', 'strawberry'])}"


SIMPLE_EXAMPLE = "This is a simple example of long text without any decoration. " * 5
MARKUP_EXAMPLE = "This is a simple example of long text with [bold]bold[/bold] and [italic]italic[/italic]."
LINK_EXAMPLE = "This is a [blue][link=https://supermegalonglink-actually-really-long-link-that-should-be-wrapped-but-very-long.com?random_param=1234567890&random_param2=1234567890]https://supermegalonglink-actually-really-long-link-that-should-be-wrapped-but-very-long.com?random_param=1234567890&random_param2=1234567890[/link][/blue]"

for style in [TaggedStyle(tag_width=7), FancyStyle()]:
    theme = RichToolkitTheme(
        style=style,
        theme={
            "tag.title": "black on #A7E3A2",
            "tag": "white on #893AE3",
            "placeholder": "grey85",
            "text": "white",
            "selected": "green",
            "result": "grey85",
            "progress": "on #893AE3",
        },
    )

    with RichToolkit(theme=theme) as app:
        app.print_title("Wrapping examples", tag="wrap")

        app.print_line()

        app.print(SIMPLE_EXAMPLE)

        app.print_line()

        app.print(MARKUP_EXAMPLE)

        app.print_line()

        app.print(LINK_EXAMPLE)

        app.print_line()

    rich.print("---------------------------")

print("RICH EXAMPLES")

rich.print()

rich.print(SIMPLE_EXAMPLE)

rich.print()

rich.print(MARKUP_EXAMPLE)

rich.print()
