from rich.color import Color

from rich_toolkit import App
from rich_toolkit.app_style import FancyAppStyle


def test_basic_usage():
    app = App(style=FancyAppStyle(base_color="#079587", title_color="#94E59A"))

    assert app.base_color == Color.parse("#079587")
