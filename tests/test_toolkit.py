from io import StringIO

import pytest
from _pytest.capture import CaptureFixture
from inline_snapshot import snapshot
from rich.console import Console
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


def test_progress_can_preserve_logs_without_wrapping() -> None:
    output = StringIO()
    console = Console(file=output, width=20, color_system=None)
    style = MinimalStyle(theme={})
    style.console = console
    app = RichToolkit(style=style, preserve_progress_logs=True)
    message = "LONG_LOG=" + "x" * 40

    with app.progress("Loading", inline_logs=True) as progress:
        progress.log(message)

    assert message in output.getvalue().splitlines()


def test_preserved_inline_progress_uses_updated_title() -> None:
    output = StringIO()
    console = Console(file=output, color_system=None)
    style = MinimalStyle(theme={})
    style.console = console
    app = RichToolkit(style=style, preserve_progress_logs=True)

    with app.progress("Loading", inline_logs=True) as progress:
        progress.log("Building...")
        progress.title = "Build complete!"

    assert output.getvalue().splitlines() == ["Building...", "Build complete!"]


def test_preserved_inline_progress_keeps_explicit_current_message() -> None:
    progress = Progress(
        "Loading",
        style=MinimalStyle(theme={}),
        inline_logs=True,
        preserve_logs=True,
    )
    progress.current_message = "Custom final message"

    progress.title = "Build complete!"

    assert progress.current_message == "Custom final message"


def test_progress_preserves_logs_in_ci_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CI", "true")
    output = StringIO()
    console = Console(
        file=output,
        width=20,
        force_terminal=True,
        color_system=None,
    )
    style = MinimalStyle(theme={})
    style.console = console
    app = RichToolkit(style=style)
    message = "LONG_LOG=" + "x" * 40

    with app.progress("Loading", inline_logs=True) as progress:
        progress.log(message)

    assert message in output.getvalue()


def test_progress_preserves_logs_for_non_interactive_output_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CI", raising=False)
    output = StringIO()
    console = Console(
        file=output,
        width=20,
        force_terminal=False,
        color_system=None,
    )
    style = MinimalStyle(theme={})
    style.console = console
    app = RichToolkit(style=style)
    message = "LONG_LOG=" + "x" * 40

    with app.progress("Loading", inline_logs=True) as progress:
        progress.log(message)

    assert message in output.getvalue().splitlines()


def test_progress_uses_live_logs_for_interactive_output_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CI", raising=False)
    output = StringIO()
    console = Console(
        file=output,
        force_terminal=True,
        color_system=None,
    )
    style = MinimalStyle(theme={})
    style.console = console
    app = RichToolkit(style=style)
    progress = app.progress("Loading", inline_logs=True)

    progress.log("Stored log")

    assert [line.text for line in progress.logs] == ["Stored log"]


def test_progress_log_preservation_can_be_disabled_globally_in_ci(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CI", "true")
    app = RichToolkit(
        style=MinimalStyle(theme={}),
        preserve_progress_logs=False,
    )

    with app.progress("Loading", inline_logs=True) as progress:
        progress.log("Stored log")

    assert [line.text for line in progress.logs] == ["Stored log"]


def test_global_progress_log_preservation_can_be_overridden() -> None:
    app = RichToolkit(
        style=MinimalStyle(theme={}),
        preserve_progress_logs=True,
    )
    progress = app.progress(
        "Loading",
        inline_logs=True,
        preserve_logs=False,
    )

    progress.log("Stored log")

    assert [line.text for line in progress.logs] == ["Stored log"]


def test_preserved_progress_log_is_quiet() -> None:
    output = StringIO()
    console = Console(file=output, width=20, color_system=None)
    style = MinimalStyle(theme={})
    style.console = console
    app = RichToolkit(style=style, mode="json", preserve_progress_logs=True)

    with app.progress("Loading") as progress:
        progress.log("LONG_LOG=" + "x" * 40)

    assert output.getvalue() == ""


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
