import random
import time

from rich_toolkit import RichToolkit, RichToolkitTheme
from rich_toolkit.styles.border import BorderedStyle
from rich_toolkit.styles.fancy import FancyStyle
from rich_toolkit.styles.tagged import TaggedStyle


def random_name_generator() -> str:
    return f"{random.choice(['fancy', 'cool', 'awesome'])}-{random.choice(['banana', 'apple', 'strawberry'])}"


theme = {
    "tag.title": "black on #A7E3A2",
    "tag": "white on #893AE3",
    "placeholder": "grey85",
    "text": "white",
    "selected": "green",
    "result": "grey85",
    "progress": "on #893AE3",
}

for style in [
    TaggedStyle(tag_width=10, theme=theme),
    FancyStyle(theme=theme),
    BorderedStyle(theme=theme),
]:
    with RichToolkit(style=style) as app:
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
                progress.log(f"Step {x} done")
