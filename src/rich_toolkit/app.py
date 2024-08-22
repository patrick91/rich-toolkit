from typing import List

from rich.color import Color
from rich.console import Console
from rich.padding import Padding

from .input import Input
from .menu import Menu, Option, ReturnValue
from .progress import Progress
from .row import RowWithTitle


class App:
    def __init__(self, base_color: str = "#f7393d") -> None:
        self.console = Console()
        self.base_color = Color.parse(base_color)

    def __enter__(self):
        self.console.print()
        return self

    def __exit__(self, *args, **kwargs):
        self.console.print()

    def print_title(self, title: str, tag: str) -> None:
        row = RowWithTitle(tag, title, base_color=self.base_color)

        self.console.print(Padding(row, (0, 0, 1, 0)))

    def confirm(self, title: str, tag: str) -> bool:
        return self.ask(
            title=title,
            tag=tag,
            options=[{"value": True, "name": "Yes"}, {"value": False, "name": "No"}],
        )

    def ask(
        self, title: str, tag: str, options: List[Option[ReturnValue]]
    ) -> ReturnValue:
        menu = Menu(
            title=title,
            tag=tag,
            options=options,
            console=self.console,
            base_color=self.base_color,
        )

        value = menu.ask()

        self.console.print()

        return value

    def input(self, title: str, tag: str, default: str = "") -> str:
        return Input(
            console=self.console,
            tag=tag,
            title=title,
            default=default,
            base_color=self.base_color,
        ).ask()

    def progress(self, title: str) -> Progress:
        return Progress(title=title, console=self.console, base_color=self.base_color)
