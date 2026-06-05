import pytest
from _pytest.capture import CaptureFixture
from inline_snapshot import snapshot
from rich.tree import Tree

from rich_toolkit import RichToolkit
from rich_toolkit.menu import Menu
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


def test_minimal_style_context_manager_does_not_print_padding(
    capsys: CaptureFixture[str],
) -> None:
    app = RichToolkit(style=MinimalStyle(theme={}))

    with app:
        pass

    captured = capsys.readouterr()

    assert captured.out == snapshot("")


def test_style_controls_context_manager_padding(capsys: CaptureFixture[str]) -> None:
    class ContextPaddingStyle(MinimalStyle):
        def render_context_enter(self):
            return "enter"

        def render_context_exit(self):
            return "exit"

    app = RichToolkit(style=ContextPaddingStyle(theme={}))

    with app:
        pass

    captured = capsys.readouterr()

    assert captured.out == snapshot("enter\nexit\n")


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


def test_inline_progress_log_splits_embedded_newlines() -> None:
    progress = Progress("Loading", style=MinimalStyle(theme={}), inline_logs=True)

    progress.log("Downloading ", end="")
    progress.log("50%\nDone\nNext", end="")
    progress.log(" line")

    assert [line.text for line in progress.logs] == snapshot(
        ["Downloading 50%", "Done", "Next line"]
    )


def test_inline_progress_log_lines_to_show_limits_embedded_newlines() -> None:
    style = MinimalStyle(theme={})
    progress = Progress(
        "Loading",
        style=style,
        inline_logs=True,
        lines_to_show=2,
    )

    progress.log("one\ntwo\nthree\n", end="")

    result = style.render_progress(progress)

    style.console.begin_capture()
    style.console.print(result)
    output = style.console.end_capture()

    assert "one" not in output
    assert "two" in output
    assert "three" in output


def test_ask_returns_menu_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Menu, "ask", lambda self: "demo")
    app = RichToolkit(style=MinimalStyle(theme={}))

    assert app.ask("Project", [{"name": "Demo", "value": "demo"}]) == "demo"
