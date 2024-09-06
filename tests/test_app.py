from _pytest.capture import CaptureFixture
from inline_snapshot import snapshot
from rich.theme import Theme
from rich.tree import Tree

from rich_toolkit import App
from rich_toolkit.app import AppTheme
from rich_toolkit.app_style import FancyAppStyle


theme = AppTheme(style=FancyAppStyle(), theme={})

def test_print_line(capsys: CaptureFixture[str]) -> None:
    app = App(theme=theme)

    app.print_line()

    captured = capsys.readouterr()

    assert captured.out == snapshot(
        """\
│
"""
    )


def test_can_print_strings(capsys: CaptureFixture[str]) -> None:
    app = App(theme=theme)

    app.print("Hello, World!")

    captured = capsys.readouterr()

    assert captured.out == snapshot(
        """\
◆ Hello, World!
"""
    )


def test_can_print_renderables(capsys: CaptureFixture[str]) -> None:
    app = App(theme=theme)

    tree = Tree("root")
    tree.add("child")

    app.print(tree)

    captured = capsys.readouterr()

    assert captured.out == snapshot(
        """\
◆ root
└ └── child
"""
    )


def test_can_print_multiple_renderables(capsys: CaptureFixture[str]) -> None:
    app = App(theme=theme)

    tree = Tree("root")
    tree.add("child")

    app.print(tree, "Hello, World!")

    captured = capsys.readouterr()

    assert captured.out == snapshot(
        """\
◆ root
└ └── child
◆ Hello, World!
"""
    )
