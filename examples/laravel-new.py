import random
import time
from typing import Any, Generator, Iterable, List

from rich._loop import loop_first_last
from rich.console import Console
from rich.segment import Segment

from rich_toolkit import RichToolkit, RichToolkitTheme
from rich_toolkit.styles.base import ANIMATION_STATUS, BaseStyle

LOGO = r""" _                               _
| |                             | |
| |     __ _ _ __ __ ___   _____| |
| |    / _` |  __/ _` \ \ / / _ \ |
| |___| (_| | | | (_| |\ V /  __/ |
|______\__,_|_|  \__,_| \_/ \___|_|
"""


class StrawberryStyle(BaseStyle):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.cursor_offset = 2

    def decorate(
        self,
        console: Console,
        lines: Iterable[List[Segment]],
        animation_status: ANIMATION_STATUS = "no_animation",
        **metadata: Any,
    ) -> Generator[Segment, None, None]:
        for first, last, line in loop_first_last(lines):
            if first:
                decoration = " " if metadata.get("title", False) else " "
            elif last:
                decoration = " "
            else:
                decoration = " "

            yield Segment(decoration)
            yield from line

            if not last:
                yield Segment.line()


with RichToolkit(
    theme=RichToolkitTheme(
        style=StrawberryStyle(),
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
) as app:
    app.print(f"[red]{LOGO}[/red]")

    app.print_line()

    app_name = app.input(
        "What is the name of your project?",
        default="my_app",
    )

    app.print_line()

    integration = app.ask(
        "Which starter kit would you like to install?",
        options=[
            {"name": "None", "value": "none"},
            {"name": "React", "value": "react"},
            {"name": "Vue", "value": "vue"},
            {"name": "Livewire", "value": "livewire"},
        ],
    )

    app.print_line()

    with app.progress("Downloading template...") as progress:
        for x in range(10):
            time.sleep(random.uniform(0.05, 0.35))

    app.print_line()

    app.print("Done!")
