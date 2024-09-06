from _pytest.capture import CaptureFixture
from inline_snapshot import snapshot
from rich.tree import Tree

from rich_toolkit import RichToolkit, RichToolkitTheme
from rich_toolkit.styles import TaggedStyle


theme = RichToolkitTheme(
    style=TaggedStyle(tag_width=5), theme={"tag": "on red", "progress": "on blue"}
)


def test_print_line(capsys: CaptureFixture[str]) -> None:
    app = RichToolkit(theme=theme)

    app.print_line()

    captured = capsys.readouterr()

    assert captured.out == snapshot(
        """\
 
"""
    )


def test_can_print_strings(capsys: CaptureFixture[str]) -> None:
    app = RichToolkit(theme=theme)

    app.print("Hello, World!")

    captured = capsys.readouterr()

    assert captured.out == snapshot(
        """\
       Hello, World!
"""
    )


def test_can_print_strings_with_tag(capsys: CaptureFixture[str]) -> None:
    app = RichToolkit(theme=theme)

    app.print("Hello, World!", tag="tag")

    captured = capsys.readouterr()

    assert captured.out == snapshot(
        """\
 tag   Hello, World!
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
       root
       └── child
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
       root
       └── child
       Hello, World!
"""
    )


def test_progress_handles_multiple_lines(capsys: CaptureFixture[str]) -> None:
    app = RichToolkit(theme=theme)

    with app.progress(title="hi") as progress:
        progress.log("Hello, World!\nHello, World!")

    captured = capsys.readouterr()

    assert captured.out == snapshot(
        """\
█████  Hello, World!
       Hello, World!\
"""
    )
