from rich.color import Color
from rich_toolkit import App


def test_basic_usage():
    app = App(base_color="#079587")

    assert app.base_color == Color.parse("#079587")
