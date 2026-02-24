"""Example showing the cancelled state of progress.

Run this and press Ctrl+C while the progress is running to see the cancelled state.
The tagged style will show the tag blocks in red, and "Cancelled." will be displayed.
"""

import time

from rich_toolkit import RichToolkit, RichToolkitTheme
from rich_toolkit.styles.tagged import TaggedStyle

style = TaggedStyle(tag_width=8)

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
    app.print_title("Cancelled progress example", tag="demo")
    app.print_line()

    with app.progress("Installing dependencies") as progress:
        for i in range(10):
            time.sleep(0.5)
            progress.log(f"Installing package {i + 1}/10...")
