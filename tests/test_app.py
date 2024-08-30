from _pytest.capture import CaptureFixture
from inline_snapshot import snapshot

from rich_toolkit import App
from rich_toolkit.app_style import FancyAppStyle


def test_print_line(capsys: CaptureFixture[str]) -> None:
    app = App(style=FancyAppStyle(base_color="#079587", title_color="#94E59A"))

    app.print_line()

    captured = capsys.readouterr()

    assert captured.out == snapshot("│\n")
