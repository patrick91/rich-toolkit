import random
import time

from rich_toolkit import App
from rich_toolkit.app_style import FancyAppStyle, TaggedAppStyle


def random_name_generator() -> str:
    return f"{random.choice(['fancy', 'cool', 'awesome'])}-{random.choice(['banana', 'apple', 'strawberry'])}"


app_style = TaggedAppStyle(base_color="#9334EB", title_color="#94E59A", tag_width=7)
app_style_fancy = FancyAppStyle(
    base_color="#9334EB", title_color="#94E59A", tag_width=7
)

for style in [app_style, app_style_fancy]:
    with App(style=style) as app:
        app.print_title("Launch sequence initiated.", tag="astro")

        app.print_line()

        app_name = app.input(
            "Where should we create your new project?",
            tag="dir",
            default=f"./{random_name_generator()}",
        )

        app.print_line()

        template = app.ask(
            "How would you like to start your new project?",
            tag="tmpl",
            options=[
                {"value": "with-samples", "name": "Include sample files"},
                {"value": "blog", "name": "Use blog template"},
                {"value": "empty", "name": "Empty"},
            ],
        )

        app.print_line()

        ts = app.confirm("Do you plan to write TypeScript?", tag="ts")

        app.print_line()

        with app.progress("Some demo here") as progress:
            for x in range(3):
                time.sleep(1)
