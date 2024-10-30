import pytest
from _pytest.capture import CaptureFixture
from inline_snapshot import snapshot
from rich.tree import Tree

from rich_toolkit import RichToolkit, RichToolkitTheme
from rich_toolkit.styles import FancyStyle


theme = RichToolkitTheme(style=FancyStyle(), theme={})


def test_print_line(capsys: CaptureFixture[str]) -> None:
    app = RichToolkit(theme=theme)

    app.print_line()

    captured = capsys.readouterr()

    assert captured.out == snapshot(
        """\
│
"""
    )


def test_can_print_strings(capsys: CaptureFixture[str]) -> None:
    app = RichToolkit(theme=theme)

    app.print("Hello, World!")

    captured = capsys.readouterr()

    assert captured.out == snapshot(
        """\
◆ Hello, World!
"""
    )


def test_can_print_renderables(capsys: CaptureFixture[str]) -> None:
    app = RichToolkit(theme=theme)

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
    app = RichToolkit(theme=theme)

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


def test_handles_keyboard_interrupt(capsys: CaptureFixture[str]) -> None:
    app = RichToolkit(theme=theme)

    with app:
        raise KeyboardInterrupt()

    captured = capsys.readouterr()

    assert captured.out == snapshot(
        """\

"""
    )

def test_ignores_keyboard_interrupt(capsys: CaptureFixture[str]) -> None:
    app = RichToolkit(theme=theme, handle_keyboard_interrupts=False)

    with pytest.raises(KeyboardInterrupt):
        with app:
            raise KeyboardInterrupt()
