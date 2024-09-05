import random
import time

from rich_toolkit import App, AppTheme
from rich_toolkit.app_style import FancyAppStyle, TaggedAppStyle


def random_name_generator() -> str:
    return f"{random.choice(['fancy', 'cool', 'awesome'])}-{random.choice(['banana', 'apple', 'strawberry'])}"


app_style = TaggedAppStyle(tag_width=7)
app_style_fancy = FancyAppStyle()

for style in [app_style, app_style_fancy]:
    app_theme = AppTheme(
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

    with App(theme=app_theme) as app:
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
