from typing import Any, List

from rich.console import Console
from rich.theme import Theme

from .app_style import AppStyle
from .input import Input
from .menu import Menu, Option, ReturnValue
from .progress import Progress


class App:
    def __init__(self, style: AppStyle, theme: Theme) -> None:
        self.console = Console(theme=theme)
        self.style = style

    def __enter__(self):
        self.console.print()
        return self

    def __exit__(self, *args, **kwargs):
        self.console.print()

    def print_title(self, title: str, **metadata: Any) -> None:
        self.console.print(self.style.with_decoration(title, title=True, **metadata))

    def print(self, text: str, **metadata: Any) -> None:
        self.console.print(self.style.with_decoration(text, **metadata))

    def print_as_string(self, text: str, **metadata: Any) -> str:
        with self.console.capture() as capture:
            self.print(text, **metadata)

        return capture.get().rstrip()

    def print_line(self) -> None:
        self.console.print(self.style.empty_line())

    def confirm(self, title: str, **metadata: Any) -> bool:
        return self.ask(
            title=title,
            options=[{"value": True, "name": "Yes"}, {"value": False, "name": "No"}],
            inline=True,
            **metadata,
        )

    def ask(
        self,
        title: str,
        options: List[Option[ReturnValue]],
        inline: bool = False,
        **metadata: Any,
    ) -> ReturnValue:
        return Menu(
            title=title,
            options=options,
            console=self.console,
            style=self.style,
            inline=inline,
            **metadata,
        ).ask()

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
