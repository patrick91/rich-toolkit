from __future__ import annotations

from rich_toolkit.button import Button
from rich_toolkit.container import Container
from rich_toolkit.element import Element
from rich_toolkit.input import Input
from rich_toolkit.menu import Menu, Option
from rich_toolkit.progress import Progress


def _make_options() -> list[Option[str]]:
    return [Option(name="A", value="a"), Option(name="B", value="b")]


def test_element_metadata_defaults_to_empty():
    element = Element()
    assert element.metadata == {}


def test_element_metadata_is_set():
    element = Element(metadata={"key": "value"})
    assert element.metadata == {"key": "value"}


def test_progress_metadata():
    progress = Progress(title="Loading", foo="bar", baz=42)
    assert progress.metadata == {"foo": "bar", "baz": 42}


def test_progress_metadata_empty():
    progress = Progress(title="Loading")
    assert progress.metadata == {}


def test_menu_metadata():
    menu = Menu("Pick", _make_options(), tag="test", level=3)
    assert menu.metadata == {"tag": "test", "level": 3}


def test_menu_metadata_empty():
    menu = Menu("Pick", _make_options())
    assert menu.metadata == {}


def test_input_metadata():
    inp = Input(label="Name", tag="input", priority=1)
    assert inp.metadata == {"tag": "input", "priority": 1}


def test_input_metadata_empty():
    inp = Input(label="Name")
    assert inp.metadata == {}


def test_button_metadata():
    button = Button(name="ok", label="OK", tag="primary")
    assert button.metadata == {"tag": "primary"}


def test_button_metadata_empty():
    button = Button(name="ok", label="OK")
    assert button.metadata == {}


def test_container_metadata():
    container = Container(metadata={"section": "form"})
    assert container.metadata == {"section": "form"}


def test_container_metadata_empty():
    container = Container()
    assert container.metadata == {}
