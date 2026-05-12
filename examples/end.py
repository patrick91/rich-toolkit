import time

from rich_toolkit import RichToolkit
from rich_toolkit.styles.border import BorderedStyle
from rich_toolkit.styles.fancy import FancyStyle
from rich_toolkit.styles.tagged import TaggedStyle

theme = {
    "tag.title": "black on #A7E3A2",
    "tag": "white on #893AE3",
    "placeholder": "grey85",
    "text": "white",
    "selected": "green",
    "result": "grey85",
    "progress": "on #893AE3",
    "error": "red",
}

for style in [
    TaggedStyle(tag_width=10, theme=theme),
    FancyStyle(theme=theme),
    BorderedStyle(theme=theme),
]:
    with RichToolkit(style=style) as app:
        app.print_title("Print without newlines", tag="demo")
        app.print_line()

        app.print("Creating ", end="")
        time.sleep(0.4)
        app.print("project ", end="")
        time.sleep(0.4)
        app.print("done", tag="result")

        app.print_line()

        with app.progress(
            "Progress logs without newlines",
            inline_logs=True,
            lines_to_show=4,
        ) as progress:
            for step in ["Resolving", "Downloading", "Installing", "Finalizing"]:
                progress.log(f"{step} ", end="")
                time.sleep(0.3)
                progress.log("done")
                time.sleep(0.2)

    print("----------------------------------------")
