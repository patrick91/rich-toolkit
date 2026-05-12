import pytest
from _pytest.capture import CaptureFixture
from inline_snapshot import snapshot
from rich.tree import Tree

from rich_toolkit import RichToolkit
from rich_toolkit.progress import Progress
from rich_toolkit.styles import FancyStyle, MinimalStyle
from ._utils import trim_whitespace_on_lines

style = FancyStyle(theme={})


def test_print_line(capsys: CaptureFixture[str]) -> None:
    app = RichToolkit(style=style)

    app.print_line()

    captured = capsys.readouterr()

    assert trim_whitespace_on_lines(captured.out) == snapshot("│")


def test_can_print_strings(capsys: CaptureFixture[str]) -> None:
    app = RichToolkit(style=style)

    app.print("Hello, World!")

    captured = capsys.readouterr()

    assert trim_whitespace_on_lines(captured.out) == snapshot("◆ Hello, World!")


def test_can_print_without_newline(capsys: CaptureFixture[str]) -> None:
    app = RichToolkit(style=MinimalStyle(theme={}))

    app.print("Hello, ", end="")
    app.print("World!")

    captured = capsys.readouterr()

    assert captured.out == snapshot("Hello, World!\n")


def test_can_print_renderables(capsys: CaptureFixture[str]) -> None:
    app = RichToolkit(style=style)

    tree = Tree("root")
    tree.add("child")

    app.print(tree)

    captured = capsys.readouterr()

    assert trim_whitespace_on_lines(captured.out) == snapshot(
        """\
◆ root
└ └── child\
"""
    )


def test_can_print_multiple_renderables(capsys: CaptureFixture[str]) -> None:
    app = RichToolkit(style=style)

    tree = Tree("root")
    tree.add("child")

    app.print(tree, "Hello, World!")

    captured = capsys.readouterr()

    assert trim_whitespace_on_lines(captured.out) == snapshot(
        """\
◆ root
└ └── child\
"""
    )


def test_handles_keyboard_interrupt(capsys: CaptureFixture[str]) -> None:
    app = RichToolkit(style=style)

    with app:
        raise KeyboardInterrupt()

    captured = capsys.readouterr()

    assert trim_whitespace_on_lines(captured.out) == snapshot("")


def test_ignores_keyboard_interrupt(capsys: CaptureFixture[str]) -> None:
    app = RichToolkit(style=style, handle_keyboard_interrupts=False)

    with pytest.raises(KeyboardInterrupt):
        with app:
            raise KeyboardInterrupt()


def test_progress_log_can_append_without_newline() -> None:
    progress = Progress("Loading", style=MinimalStyle(theme={}))

    progress.log("Downloading ", end="")
    progress.log("50%")
    assert progress.current_message == snapshot("Downloading 50%")

    progress.log("Done")
    assert progress.current_message == snapshot("Done")


def test_inline_progress_log_can_append_without_newline() -> None:
    progress = Progress("Loading", style=MinimalStyle(theme={}), inline_logs=True)

    progress.log("Downloading ", end="")
    progress.log("50%")
    progress.log("Done")

    assert [line.text for line in progress.logs] == snapshot(
        ["Downloading 50%", "Done"]
    )
