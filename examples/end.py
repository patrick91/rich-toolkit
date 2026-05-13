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
            "Progress logs with partial and multiline output",
            inline_logs=True,
            lines_to_show=6,
        ) as progress:
            for i in range(8):
                progress.log(f"Resolving project {i} ", end="")
                time.sleep(0.2)
                if i == 6:
                    progress.log("packages\nInstalling dependencies\nWriting lockfile")
                else:
                    progress.log("done")
                time.sleep(0.2)

        app.print_line()

        with app.progress("Multiline progress message") as progress:
            progress.log("Preparing workspace\nInstalling packages")
            time.sleep(0.5)

    print("----------------------------------------")
