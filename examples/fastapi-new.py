import random
import time
from typing import Any, Generator, Iterable, List

from rich._loop import loop_first_last
from rich.console import Console
from rich.segment import Segment

from rich_toolkit import RichToolkit, RichToolkitTheme
from rich_toolkit.styles.base import ANIMATION_STATUS, BaseStyle


class StrawberryStyle(BaseStyle):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.cursor_offset = 3

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
    app.print_title("strawberry")
    app.print_line()

    app.print("""
          ░░▒▒▒▒░░
      ░▒▒▒▒▒▒▒░░▒▒▒▒▒░
    ▒▒▒▒▒▒▒▒▒░  ▒▒▒▒▒▒▒▒
  ░▒▒▒▒▒▒▒▒▒░   ▒▒▒▒▒▒▒▒▒░
 ░▒▒▒▒▒▒▒▒▒░    ▒▒▒▒▒▒▒▒▒▒░
 ▒▒▒▒▒▒▒▒▒▒     ▒▒▒▒▒▒▒▒▒▒▒
░▒▒▒▒▒▒▒▒▒          ░▒▒▒▒▒▒▒
▒▒▒▒▒▒▒▒▒          ░▒▒▒▒▒▒▒▒
░▒▒▒▒▒▒▒           ▒▒▒▒▒▒▒▒▒
 ▒▒▒▒▒▒▒▒▒▒▒░     ▒▒▒▒▒▒▒▒▒
 ░▒▒▒▒▒▒▒▒▒▒░    ▒▒▒▒▒▒▒▒▒░
  ░▒▒▒▒▒▒▒▒▒░   ▒▒▒▒▒▒▒▒▒░
    ▒▒▒▒▒▒▒▒░  ▒▒▒▒▒▒▒▒▒
      ░▒▒▒▒▒░░▒▒▒▒▒▒▒░
          ░░▒▒▒▒░░
""")

    app.print_line()

    app_name = app.input(
        "What is the name of your app? >",
        inline=True,
        default="my_app",
    )

    app.print_line()

    integration = app.ask(
        "What integration do you want to use?",
        options=[
            {"name": "FastAPI", "value": "fastapi"},
            {"name": "Starlette", "value": "starlette"},
            {"name": "Tornado", "value": "tornado"},
            {"name": "Django", "value": "django"},
            {"name": "Flask", "value": "flask"},
        ],
    )

    app.print_line()

    with app.progress("Downloading template...") as progress:
        for _ in range(10):
            time.sleep(random.uniform(0.05, 0.35))

    app.print_line()

    app.print("Done!")
