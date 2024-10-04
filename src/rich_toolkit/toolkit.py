from typing import Any, Dict, List

from rich.console import Console, RenderableType
from rich.theme import Theme

from .styles.base import BaseStyle
from .input import Input
from .menu import Menu, Option, ReturnValue
from .progress import Progress


class RichToolkitTheme:
    def __init__(self, style: BaseStyle, theme: Dict[str, str]) -> None:
        self.style = style
        self.rich_theme = Theme(theme)


class RichToolkit:
    def __init__(self, theme: RichToolkitTheme) -> None:
        self.console = Console(theme=theme.rich_theme)
        self.theme = theme

    def __enter__(self):
        self.console.print()
        return self

    def __exit__(self, *args, **kwargs):
        self.console.print()

    def print_title(self, title: str, **metadata: Any) -> None:
        self.console.print(
            self.theme.style.with_decoration(title, title=True, **metadata)
        )

    def print(self, *renderables: RenderableType, **metadata: Any) -> None:
        self.console.print(self.theme.style.with_decoration(*renderables, **metadata))

    def print_as_string(self, *renderables: RenderableType, **metadata: Any) -> str:
        with self.console.capture() as capture:
            self.print(*renderables, **metadata)

        return capture.get().rstrip()

    def print_line(self) -> None:
        self.console.print(self.theme.style.empty_line())

    def confirm(self, title: str, **metadata: Any) -> bool:
        return self.ask(
            title=title,
            options=[
                Option({"value": True, "name": "Yes"}),
                Option({"value": False, "name": "No"}),
            ],
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
            style=self.theme.style,
            inline=inline,
            **metadata,
        ).ask()

    def input(
        self, title: str, default: str = "", password: bool = False, **metadata: Any
    ) -> str:
        return Input(
            console=self.console,
            style=self.theme.style,
            title=title,
            default=default,
            cursor_offset=self.theme.style.cursor_offset,
            password=password,
            **metadata,
        ).ask()

    def progress(
        self, title: str, transient: bool = False, transient_on_error: bool = False
    ) -> Progress:
        return Progress(
            title=title,
            console=self.console,
            style=self.theme.style,
            transient=transient,
            transient_on_error=transient_on_error,
        )
