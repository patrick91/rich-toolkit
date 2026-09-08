from __future__ import annotations

import codecs
import io
import json
import sys
from contextlib import contextmanager

import pytest
from rich.align import Align
from rich.console import Group
from rich.control import Control
from rich.padding import Padding
from rich.panel import Panel
from rich.segment import Segment
from rich.style import Style
from rich.table import Table
from rich.text import Text

from rich_toolkit import RichToolkit
from rich_toolkit._console import ToolkitConsole, prepare_text
from rich_toolkit.container import Container
from rich_toolkit.input import Input
from rich_toolkit.menu import Menu, Option
from rich_toolkit.styles import BorderedStyle, FancyStyle, MinimalStyle, TaggedStyle

STYLES = [MinimalStyle, TaggedStyle, BorderedStyle, FancyStyle]


def test_suite_capture_enforces_the_requested_encoding(capsys, output_encoding):
    value = "café 项目 🚀".encode(output_encoding, "replace").decode(output_encoding)
    for stream in (sys.stdout, sys.stderr):
        assert codecs.lookup(stream.encoding) == codecs.lookup(output_encoding)
        assert stream.errors == "strict"
        stream.write(value)
        stream.flush()
        assert stream.buffer.getvalue() == value.encode(output_encoding)

    captured = capsys.readouterr()
    assert captured.out == value
    assert captured.err == value
    assert capsys.readouterr() == ("", "")

    if output_encoding in ("ascii", "cp1252", "gbk"):
        for stream in (sys.stdout, sys.stderr):
            with pytest.raises(UnicodeEncodeError):
                stream.write("🚀")


@contextmanager
def encoded_toolkit(encoding, style_type=MinimalStyle, *, terminal=False, width=80):
    with io.TextIOWrapper(io.BytesIO(), encoding=encoding, errors="strict") as stream:
        style = style_type()
        style.console = ToolkitConsole(
            file=stream,
            theme=style.theme,
            force_terminal=terminal,
            color_system=None,
            width=width,
        )
        yield RichToolkit(style=style), stream


def read_output(stream):
    stream.flush()
    return stream.buffer.getvalue().decode(stream.encoding)


@pytest.mark.parametrize("style_type", STYLES)
def test_arbitrary_content_can_be_printed(output_encoding, style_type):
    original = "café 项目 🚀"
    with encoded_toolkit(output_encoding, style_type) as (toolkit, stream):
        toolkit.print(original)
        toolkit.print(Text(original, style="bold"))
        toolkit.print(Group(Text(original), Text("second line")))
        toolkit.print_line()
        output = read_output(stream)

        expected = original.encode(output_encoding, "replace").decode(output_encoding)
        assert expected in output
        assert "second line" in output
        assert stream.errors == "strict"
        assert stream.encoding == output_encoding


def test_replacement_preserves_styles_links_and_original_text():
    original = Text.assemble(("🚀", "bold"), (" docs", "link https://example.com"))
    prepared = prepare_text(original, "cp1252")

    assert prepared.plain == "? docs"
    assert prepared.spans == original.spans
    assert original.plain == "🚀 docs"
    assert original.spans[1].start == 1
    assert prepare_text(original, "utf-8") is original


def test_replacement_happens_before_wrapping():
    with encoded_toolkit("cp1252", width=4) as (toolkit, stream):
        toolkit.print(Text("🚀abc", overflow="fold"))
        assert read_output(stream) == "?abc\n"


def test_table_cells_wrap_replaced_text_without_mutating_values():
    value = Text("🚀abc")
    table = Table.grid()
    table.add_column(width=3, overflow="fold")
    table.add_column(width=3)
    table.add_row(value, "end")
    with encoded_toolkit("cp1252") as (toolkit, stream):
        toolkit.print(table)
        assert read_output(stream) == "?abend\nc     \n"
        assert value.plain == "🚀abc"


@pytest.mark.parametrize(
    "wrap", [lambda value: value, Group, lambda value: Padding(value, 0)]
)
def test_auto_sized_table_cells_measure_replaced_text(wrap):
    value = Text("🚀abc", style="bold")
    cell = wrap(value)
    table = Table.grid()
    table.add_row(cell, "end")
    with encoded_toolkit("cp1252") as (toolkit, stream):
        assert toolkit.console.measure(cell).maximum == 4
        assert toolkit.console.measure(table).maximum == 7
        toolkit.print(table)
        assert read_output(stream) == "?abcend\n"
        assert value.plain == "🚀abc"
        assert next(table.columns[0].cells) is cell


def test_auto_sized_table_headers_and_footers_measure_replaced_text():
    header = Text("🚀abc")
    footer = Text("🐔xyz")
    table = Table(box=None, padding=0, show_footer=True)
    table.add_column(header=header, footer=footer)
    table.add_row("body")
    with encoded_toolkit("cp1252") as (toolkit, stream):
        toolkit.print(table)
        assert [line.rstrip() for line in read_output(stream).splitlines()] == [
            "?abc",
            "body",
            "?xyz",
        ]
        assert table.columns[0].header is header
        assert table.columns[0].footer is footer


def test_nested_table_can_be_reused_with_different_encodings():
    value = Text("🚀abc", style="bold")
    table = Table.grid()
    table.add_row(Padding(Group(value), 0), "end")
    panel = Panel.fit(table, title="[bold]🚀[/]")

    for encoding, expected in (
        (
            "cp1252",
            "+--- ? ---+\n| ?abcend |\n+---------+\n",
        ),
        ("utf-8", "╭─── 🚀 ───╮\n│ 🚀abcend │\n╰──────────╯\n"),
    ):
        with encoded_toolkit(encoding) as (toolkit, stream):
            toolkit.print(Align.left(panel, pad=False))
            assert read_output(stream) == expected

    assert value.plain == "🚀abc"
    assert panel.title == "[bold]🚀[/]"


def test_unicode_hyperlinks_remain_clickable_without_mutating_styles(output_encoding):
    link = "https://example.com/café/🚀?q=%20&next=/docs#section"
    expected = (
        link
        if output_encoding == "utf-8"
        else "https://example.com/caf%C3%A9/%F0%9F%9A%80?q=%20&next=/docs#section"
    )
    style = Style(bold=True, link=link)
    value = Text("docs", style=style)

    class CustomRenderable:
        def __rich_console__(self, console, options):
            yield Segment("raw", style)

    with io.TextIOWrapper(
        io.BytesIO(), encoding=output_encoding, errors="strict"
    ) as stream:
        console = ToolkitConsole(
            file=stream, force_terminal=True, color_system="standard"
        )
        console.print(value)
        console.print(CustomRenderable())
        output = read_output(stream)
        assert output.count(expected + "\x1b\\") == 2
        assert "\x1b[1mdocs\x1b[0m" in output
        assert "\x1b[1mraw\x1b[0m" in output
        assert style.link == link
        assert value.style is style


def test_direct_segments_have_a_fallback_and_controls_are_preserved():
    class CustomRenderable:
        def __rich_console__(self, console, options):
            yield Segment("🐔", style=console.get_style("bold"))
            yield Control.move_to_column(3).segment

    with encoded_toolkit("cp1252", terminal=True) as (toolkit, stream):
        segments = list(toolkit.console.render(CustomRenderable()))
        assert segments[0].text == "?"
        assert segments[0].style.bold
        assert segments[1] == Control.move_to_column(3).segment
        toolkit.print(CustomRenderable())
        assert "?" in read_output(stream)


def test_rich_cast_text_is_replaced_before_wrapping():
    class CustomText:
        def __rich__(self):
            return Text("🚀abc", overflow="fold")

    with encoded_toolkit("cp1252", width=4) as (toolkit, stream):
        toolkit.console.print(CustomText())
        assert read_output(stream) == "?abc\n"


@pytest.mark.parametrize("style_type", STYLES)
def test_menu_navigation_returns_original_values(
    output_encoding, style_type, monkeypatch
):
    keys = iter([Menu.DOWN_KEY, Menu.ENTER_KEY])
    monkeypatch.setattr("rich_toolkit.container.getchar", lambda: next(keys))
    values = ["café 🚀", "项目 🐔"]
    with encoded_toolkit(output_encoding, style_type, terminal=True) as (
        toolkit,
        stream,
    ):
        result = toolkit.ask("Team 🚀", [Option(name=v, value=v) for v in values])
        assert result == values[1]
        assert values[1].encode(output_encoding, "replace").decode(
            output_encoding
        ) in read_output(stream)


@pytest.mark.parametrize("style_type", STYLES)
def test_editing_input_keeps_original_value_and_displayed_cursor_width(
    style_type, monkeypatch
):
    keys = iter([Input.LEFT_KEY, Input.BACKSPACE_KEY, "🐔", Input.ENTER_KEY])
    monkeypatch.setattr("rich_toolkit.container.getchar", lambda: next(keys))
    with encoded_toolkit("cp1252", style_type, terminal=True) as (toolkit, stream):
        result = toolkit.input("Name", value="a🚀b")
        assert result == "a🐔b"
        assert "a?b" in read_output(stream)

        field = Input(label="Name", value="a🚀b", style=toolkit.style)
        field.handle_key(Input.LEFT_KEY)
        assert field.cursor_offset.left == 2
        field.handle_key(Input.BACKSPACE_KEY)
        assert field.text == "ab"
        assert field.cursor_offset.left == 1


def test_filtering_uses_original_text_and_displayed_cursor_width():
    with encoded_toolkit("cp1252") as (toolkit, stream):
        menu = Menu(
            "Team",
            [Option(name="🚀", value="original")],
            allow_filtering=True,
            style=toolkit.style,
        )
        menu.handle_key("🚀")
        assert menu.options[0]["value"] == "original"
        assert menu.cursor_offset.left == len("Filter: ") + 1
        toolkit.console.print(toolkit.style.render_element(menu))
        assert "Filter: ?" in read_output(stream)


@pytest.mark.parametrize("style_type", STYLES)
def test_empty_input_and_password_do_not_expose_replacement_characters(
    style_type, monkeypatch
):
    keys = iter([Input.ENTER_KEY, Input.ENTER_KEY])
    monkeypatch.setattr("rich_toolkit.container.getchar", lambda: next(keys))
    with encoded_toolkit("cp1252", style_type, terminal=True) as (toolkit, stream):
        assert toolkit.input("Name") == ""
        assert toolkit.input("Password", value="🚀", password=True) == "🚀"
        field = Input(value="🚀", password=True, style=toolkit.style)
        assert field.cursor_offset.left == 1
        output = read_output(stream)
        assert "?" not in Text.from_ansi(output).plain


def test_empty_fancy_input_keeps_its_row_when_editing(output_encoding):
    with encoded_toolkit(output_encoding, FancyStyle, terminal=True) as (
        toolkit,
        stream,
    ):
        field = Input("Name", style=toolkit.style)
        container = Container(style=toolkit.style)
        container.elements = [field]

        for key in ("", "a", Input.BACKSPACE_KEY):
            field.handle_key(key)
            container._refresh()
            assert container._live_render._shape == (80, 2)
            assert container.get_offset_for_active_element() == 0

        assert field.text == ""
        output = read_output(stream)
        assert "\x1b[-" not in output
        assert "\u200b" not in output
        assert "?" not in Text.from_ansi(output).plain


def test_json_preserves_unicode_values(capsys):
    data = {"name": "café 项目 🚀", "literal": r"\U0001f680"}
    RichToolkit(mode="json").output(data)
    output = capsys.readouterr().out
    assert json.loads(output) == data
    assert output.isascii()


def test_ascii_menu_decorations():
    with encoded_toolkit("ascii") as (toolkit, stream):
        options = [Option(name="one", value=1), Option(name="two", value=2)]
        menu = Menu("Pick", options, style=toolkit.style)
        toolkit.console.print(toolkit.style.render_element(menu))
        assert (
            "\n".join(line.rstrip() for line in read_output(stream).splitlines())
            == "Pick\n> one\n  two"
        )
        assert toolkit.style.symbol("*", fallback="-") == "*"


@pytest.mark.parametrize("style_type", STYLES)
@pytest.mark.parametrize("preserve_logs", [False, True])
def test_progress_logs_and_completion_are_encoding_safe(style_type, preserve_logs):
    with encoded_toolkit("cp1252", style_type) as (toolkit, stream):
        with toolkit.progress(
            "Working 🚀", inline_logs=True, preserve_logs=preserve_logs
        ) as progress:
            progress.log("Building 📁")
            progress.log(Text("Ready 🐔", style="bold"))
            progress.current_message = "Done ✅"
        output = read_output(stream)
        assert "Building ?" in output
        assert "Ready ?" in output
        assert progress.current_message == "Done ✅"


def test_checkbox_selection_and_scroll_indicators(monkeypatch):
    keys = iter([" ", Menu.DOWN_KEY, " ", Menu.ENTER_KEY])
    monkeypatch.setattr("rich_toolkit.container.getchar", lambda: next(keys))
    with encoded_toolkit("ascii", terminal=True) as (toolkit, stream):
        menu = Menu(
            "Pick",
            [Option(name="🚀", value=1), Option(name="🐔", value=2)],
            style=toolkit.style,
            console=toolkit.console,
            multiple=True,
            max_visible=1,
        )
        assert menu.ask() == [1, 2]
        output = read_output(stream)
        assert "x " in output
        assert "v more" in output
        assert "^ more" in output


def test_input_label_measurement_uses_displayed_width():
    with encoded_toolkit("cp1252", width=5) as (toolkit, stream):
        field = Input(label="🚀abcd", style=toolkit.style)
        assert toolkit.style.get_cursor_offset_for_element(field).top == 2


def test_console_tracks_replaced_output_stream():
    with encoded_toolkit("utf-8") as (toolkit, utf8_stream):
        toolkit.print("🚀")
        with io.TextIOWrapper(io.BytesIO(), encoding="cp1252") as legacy_stream:
            toolkit.console.file = legacy_stream
            toolkit.print("🚀")
            assert read_output(legacy_stream) == "?\n"
        assert read_output(utf8_stream) == "🚀\n"
