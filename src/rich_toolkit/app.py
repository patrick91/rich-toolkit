from typing import Any, List

from rich.console import Console

from .app_style import AppStyle
from .input import Input
from .menu import Menu, Option, ReturnValue
from .progress import Progress
from .row import RowWithDecoration


class App:
    def __init__(self, style: AppStyle) -> None:
        self.console = Console()
        self.style = style

    def __enter__(self):
        self.console.print()
        return self

    def __exit__(self, *args, **kwargs):
        self.console.print()

    def print_title(self, title: str, **metadata: Any) -> None:
        row = RowWithDecoration(title, style=self.style, title=True, **metadata)

        self.console.print(row)

    def print_line(self) -> None:
        self.console.print(self.style.render_empty_line())

    def confirm(self, title: str, tag: str) -> bool:
        return self.ask(
            title=title,
            tag=tag,
            options=[{"value": True, "name": "Yes"}, {"value": False, "name": "No"}],
            inline=True,
        )

    def ask(
        self,
        title: str,
        tag: str,
        options: List[Option[ReturnValue]],
        inline: bool = False,
    ) -> ReturnValue:
        menu = Menu(
            title=title,
            tag=tag,
            options=options,
            console=self.console,
            style=self.style,
            inline=inline,
        )

        return menu.ask()

    def input(self, title: str, default: str = "", **metadata: Any) -> str:
        return Input(
            console=self.console,
            style=self.style,
            title=title,
            default=default,
            **metadata,
        ).ask()

    def progress(self, title: str) -> Progress:
        return Progress(
            title=title,
            console=self.console,
            style=self.style,
        )
