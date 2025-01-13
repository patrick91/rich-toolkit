import random
import time

from rich_toolkit import RichToolkit, RichToolkitTheme
from rich_toolkit.styles import FancyStyle, TaggedStyle

for style in [TaggedStyle(tag_width=8), FancyStyle()]:
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
            "error": "red",
        },
    )

    with RichToolkit(theme=theme) as app:
        app.print_title("Progress log examples", tag="demo")
        app.print_line()

        with app.progress(
            "Progress with inline logs (last 5)",
            inline_logs=True,
            lines_to_show=10,
        ) as progress:
            for x in range(50):
                time.sleep(random.uniform(0.05, 0.35))
                progress.log(f"Step {x + 1} completed")

        app.print_line()

        with app.progress(
            "Progress with inline logs",
            inline_logs=True,
        ) as progress:
            for x in range(20):
                time.sleep(random.uniform(0.05, 0.35))
                progress.log(f"Step {x + 1} completed")

    print("----------------------------------------")
