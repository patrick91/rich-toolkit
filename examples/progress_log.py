import random
import time
from typing import Any, Dict, Generator, List, Tuple

import httpx
from rich.segment import Segment
from rich.text import Text

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


def stream_data() -> Generator[str, None, None]:
    url = "http://localhost:8000/stream/"
    url = "https://httpbun.com/drip-lines"

    with httpx.Client() as client:
        with client.stream("GET", url, timeout=60) as response:
            response.raise_for_status()

            yield from response.iter_lines()


for style in [
    TaggedStyle(tag_width=10, theme=theme),
    FancyStyle(theme=theme),
    BorderedStyle(theme=theme),
]:
    with RichToolkit(style=style) as app:
        app.print_title("Progress log examples", tag="demo")
        app.print_line()

        with app.progress(
            "Progress with inline logs (http stream)",
            inline_logs=True,
            lines_to_show=4,
        ) as progress:
            for line in stream_data():
                progress.log(line)

        app.print_line()

        with app.progress(
            "Progress with logs and colors",
            inline_logs=True,
            lines_to_show=10,
        ) as progress:
            for x in range(20):
                time.sleep(random.uniform(0.05, 0.35))
                progress.log(
                    Text.from_markup(
                        f"[{x}] [green]Build[/] [blue]Summary[/] [red]red[/]: [link=http://example.com]http://example.com[/link]"
                    )
                )

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

        app.print_line()

        with app.progress(
            "Progress with inline logs",
            inline_logs=True,
        ) as progress:
            for x in range(5):
                time.sleep(1)
                progress.log(f"Step {x + 1} completed")

    print("----------------------------------------")
