from typing import Any, Dict, List

from rich.console import Console, RenderableType
from rich.theme import Theme

from .app_style import AppStyle
from .input import Input
from .menu import Menu, Option, ReturnValue
from .progress import Progress


class AppTheme:
    def __init__(self, style: AppStyle, theme: Dict[str, str]) -> None:
        self.style = style
        self.rich_theme = Theme(theme)


class App:
    def __init__(self, theme: AppTheme) -> None:
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
            style=self.theme.style,
            inline=inline,
            **metadata,
        ).ask()

    def input(self, title: str, default: str = "", **metadata: Any) -> str:
        # TODO: can we find a way to not have to pass style here? (same for menu and progress)
        return Input(
            console=self.console,
            style=self.theme.style,
            title=title,
            default=default,
            **metadata,
        ).ask()

    def progress(self, title: str) -> Progress:
        return Progress(
            title=title,
            console=self.console,
            style=self.theme.style,
        )
