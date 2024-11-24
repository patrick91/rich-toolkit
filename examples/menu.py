import random
from typing import List
from rich_toolkit import RichToolkit, RichToolkitTheme
from rich_toolkit.styles import FancyStyle, TaggedStyle
from rich_toolkit.menu import Option


words = [
    "sparkle",
    "giggle",
    "sunshine",
    "rainbow",
    "bubble",
    "cuddle",
    "twinkle",
    "flutter",
    "bounce",
    "glitter",
    "happy",
    "smile",
    "dance",
    "laugh",
    "dream",
    "wonder",
    "magic",
    "delight",
    "joy",
    "cozy",
]


def get_options() -> List[Option]:
    return [
        {"name": f"{word_1} {word_2}", "value": f"{word_1} {word_2}"}
        for word_1, word_2 in zip(
            random.choices(words, k=10), random.choices(words, k=10)
        )
    ]


for style in [TaggedStyle(tag_width=12), FancyStyle()]:
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
        app.print_title("Launch sequence initiated.", tag="astro")
        app.print_line()

        app.ask(
            "Where should we create your new project?",
            tag="dir",
            options=get_options(),
        )
        app.print_line()

        app.ask(
            "Where should we create your new project? (inline)",
            tag="dir",
            options=get_options(),
            inline=True,
        )
        app.print_line()

        app.ask(
            "Where should we create your new project? (Type to search)",
            tag="dir",
            options=get_options(),
            allow_filtering=True,
        )
        app.print_line()
