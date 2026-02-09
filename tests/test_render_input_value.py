from rich_toolkit.input import Input
from rich_toolkit.styles import MinimalStyle


style = MinimalStyle()


def test_shows_placeholder_when_not_done():
    input = Input(placeholder="Enter name")
    assert style.render_input_value(input, done=False) == "[placeholder]Enter name[/]"


def test_shows_empty_when_done_and_no_text():
    input = Input(placeholder="Enter name")
    assert style.render_input_value(input, done=True) == "[result][/]"


def test_shows_typed_text():
    input = Input(placeholder="Enter name")
    input.text = "hello"
    assert style.render_input_value(input, done=False) == "[text]hello[/]"


def test_shows_typed_text_as_result_when_done():
    input = Input(placeholder="Enter name")
    input.text = "hello"
    assert style.render_input_value(input, done=True) == "[result]hello[/]"


def test_shows_default_as_placeholder_when_not_done():
    input = Input(default="my-app", default_as_placeholder=True)
    assert style.render_input_value(input, done=False) == "[placeholder]my-app[/]"


def test_shows_default_as_result_when_done():
    input = Input(default="my-app", default_as_placeholder=True)
    assert style.render_input_value(input, done=True) == "[result]my-app[/]"


def test_shows_cancelled_placeholder():
    input = Input(placeholder="Enter name")
    input._cancelled = True
    result = style.render_input_value(input, done=False)
    assert result == "[placeholder.cancelled]Enter name[/]"


def test_shows_cancelled_with_text():
    input = Input(placeholder="Enter name")
    input.text = "hello"
    input._cancelled = True
    result = style.render_input_value(input, done=False)
    assert result == "[placeholder.cancelled]hello[/]"


def test_shows_cancelled_with_default():
    input = Input(default="my-app", default_as_placeholder=True)
    input._cancelled = True
    result = style.render_input_value(input, done=False)
    assert result == "[placeholder.cancelled]my-app[/]"


def test_cancelled_and_done_shows_cancelled():
    input = Input(placeholder="Enter name")
    input.text = "hello"
    input._cancelled = True
    result = style.render_input_value(input, done=True)
    assert result == "[placeholder.cancelled]hello[/]"


def test_password_masks_text():
    input = Input(password=True)
    input.text = "secret"
    assert style.render_input_value(input, done=False) == "[text]******[/]"


def test_password_shows_placeholder_when_empty():
    input = Input(password=True, placeholder="Enter password")
    result = style.render_input_value(input, done=False)
    assert result == "[placeholder]Enter password[/]"
