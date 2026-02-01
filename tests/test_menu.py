from __future__ import annotations

import pytest
from rich.text import Text

from rich_toolkit.menu import Menu, Option
from rich_toolkit.styles.base import BaseStyle


def _make_options(names: list[str]) -> list[Option[str]]:
    return [Option(name=n, value=n.lower()) for n in names]


OPTIONS = _make_options(["Alpha", "Beta", "Gamma"])


def _render_done_menu(menu: Menu) -> Text:
    """Render a menu in the done state and return the resulting Text."""
    style = BaseStyle()
    result = style.render_menu(menu, is_active=False, done=True, parent=None)
    assert isinstance(result, Text)
    return result


def test_multiple_and_inline_raises():
    with pytest.raises(ValueError, match="multiple and inline cannot both be True"):
        Menu("Pick", OPTIONS, inline=True, multiple=True)


def test_default_state():
    menu = Menu("Pick", OPTIONS, multiple=True)
    assert menu.checked == set()
    assert menu.selected == 0


def test_space_toggles_checked():
    menu = Menu("Pick", OPTIONS, multiple=True)
    menu.handle_key(" ")
    assert menu.checked == {0}
    menu.handle_key(" ")
    assert menu.checked == set()


def test_arrow_keys_move_cursor():
    menu = Menu("Pick", OPTIONS, multiple=True)
    down = menu.DOWN_KEY
    up = menu.UP_KEY

    menu.handle_key(down)
    assert menu.selected == 1
    assert menu.checked == set()

    menu.handle_key(up)
    assert menu.selected == 0
    assert menu.checked == set()


def test_jk_move_cursor():
    menu = Menu("Pick", OPTIONS, multiple=True)
    menu.handle_key("j")
    assert menu.selected == 1
    menu.handle_key("k")
    assert menu.selected == 0


def test_toggle_navigate_toggle_multiple_items():
    menu = Menu("Pick", OPTIONS, multiple=True)
    menu.handle_key(" ")  # check Alpha (index 0)
    menu.handle_key("j")  # move to Beta
    menu.handle_key(" ")  # check Beta (index 1)
    assert menu.checked == {0, 1}
    assert menu.selected == 1


def test_result_display_name_single():
    menu = Menu("Pick", OPTIONS)
    menu.selected = 1
    assert menu.result_display_name == "Beta"


def test_result_display_name_multiple():
    menu = Menu("Pick", OPTIONS, multiple=True)
    menu.checked = {2, 0}
    assert menu.result_display_name == "Alpha, Gamma"


def test_active_prefix_multiple():
    menu = Menu("Pick", OPTIONS, multiple=True)
    assert menu.active_prefix == "■"


def test_active_prefix_single():
    menu = Menu("Pick", OPTIONS)
    assert menu.active_prefix == "●"


def test_inactive_prefix_multiple():
    menu = Menu("Pick", OPTIONS, multiple=True)
    assert menu.inactive_prefix == "□"


def test_inactive_prefix_single():
    menu = Menu("Pick", OPTIONS)
    assert menu.inactive_prefix == "○"


def test_selection_count_hint_not_multiple():
    menu = Menu("Pick", OPTIONS)
    assert menu.selection_count_hint is None


def test_selection_count_hint_multiple_no_filtering():
    menu = Menu("Pick", OPTIONS, multiple=True)
    menu.checked = {0}
    assert menu.selection_count_hint is None


def test_selection_count_hint_multiple_with_filtering():
    menu = Menu("Pick", OPTIONS, multiple=True, allow_filtering=True)
    menu.checked = {0, 2}
    assert menu.selection_count_hint == "(2 selected)"


def test_selection_count_hint_empty_checked():
    menu = Menu("Pick", OPTIONS, multiple=True, allow_filtering=True)
    assert menu.selection_count_hint is None


def test_on_validate_no_checked_invalid():
    menu = Menu("Pick", OPTIONS, multiple=True)
    menu.on_validate()
    assert menu.valid is False


def test_on_validate_with_checked_valid():
    menu = Menu("Pick", OPTIONS, multiple=True)
    menu.checked = {1}
    menu.on_validate()
    assert menu.valid is True


def test_validation_message_when_invalid():
    menu = Menu("Pick", OPTIONS, multiple=True)
    menu.valid = False
    assert menu.validation_message == "Please select at least one option"


def test_filter_narrows_options_preserves_checked():
    menu = Menu("Pick", OPTIONS, multiple=True, allow_filtering=True)
    # Check Alpha (original index 0)
    menu.handle_key(" ")
    assert menu.checked == {0}

    # Type "be" to filter — only Beta visible
    menu.handle_key("b")
    menu.handle_key("e")
    assert len(menu.options) == 1
    assert menu.options[0]["name"] == "Beta"

    # Alpha still checked even though hidden
    assert menu.checked == {0}


def test_is_option_checked_through_filter():
    menu = Menu("Pick", OPTIONS, multiple=True, allow_filtering=True)
    # Check Beta (navigate then toggle)
    menu.handle_key(menu.DOWN_KEY)
    menu.handle_key(" ")
    assert menu.checked == {1}

    # Filter to show only Beta
    menu.handle_key("b")
    menu.handle_key("e")
    assert len(menu.options) == 1
    # Beta is at filtered index 0 and should be checked
    assert menu.is_option_checked(0) is True


def test_get_option_index_uses_identity():
    opts = _make_options(["Dup", "Dup"])  # same name & value
    menu = Menu("Pick", opts, multiple=True)
    assert menu._get_option_index(opts[0]) == 0
    assert menu._get_option_index(opts[1]) == 1


def test_filter_toggle_clear_preserves_all_checked():
    """Check items through different filter views, clear filter, verify all stay checked."""
    opts = _make_options(["Apple", "Apricot", "Banana", "Blueberry"])
    menu = Menu("Pick", opts, multiple=True, allow_filtering=True)

    # Filter to "ap" → Apple, Apricot visible
    menu.handle_key("a")
    menu.handle_key("p")
    assert [o["name"] for o in menu.options] == ["Apple", "Apricot"]

    # Toggle both filtered items
    menu.handle_key(" ")  # check Apple (filtered index 0 → original 0)
    menu.handle_key(menu.DOWN_KEY)
    menu.handle_key(" ")  # check Apricot (filtered index 1 → original 1)
    assert menu.checked == {0, 1}

    # Clear filter with backspace twice
    menu.handle_key("\x7f")
    menu.handle_key("\x7f")
    assert len(menu.options) == 4  # all options visible again

    # Filter to "b" → Banana, Blueberry
    menu.handle_key("b")
    assert [o["name"] for o in menu.options] == ["Banana", "Blueberry"]

    menu.handle_key(" ")  # check Banana (original index 2)
    assert menu.checked == {0, 1, 2}

    # Clear filter and confirm all three are still checked
    menu.handle_key("\x7f")
    assert menu.checked == {0, 1, 2}
    assert menu.is_option_checked(0) is True  # Apple
    assert menu.is_option_checked(1) is True  # Apricot
    assert menu.is_option_checked(2) is True  # Banana
    assert menu.is_option_checked(3) is False  # Blueberry


def test_scroll_and_multiselect():
    """Toggle items above and below the visible scroll window."""
    opts = _make_options(["One", "Two", "Three", "Four", "Five"])
    menu = Menu("Pick", opts, multiple=True, max_visible=2)

    # Visible window starts at [One, Two]
    menu.handle_key(" ")  # check One (index 0)
    assert menu.checked == {0}

    # Navigate down past the visible window
    menu.handle_key(menu.DOWN_KEY)  # → Two
    menu.handle_key(menu.DOWN_KEY)  # → Three (scrolls)
    menu.handle_key(menu.DOWN_KEY)  # → Four
    menu.handle_key(" ")  # check Four (index 3)
    assert menu.checked == {0, 3}
    assert menu.selected == 3

    # Scroll should have adjusted so Four is visible
    start, end = menu.visible_options_range
    assert start <= 3 < end

    # Navigate back up to One and uncheck it
    menu.handle_key(menu.UP_KEY)  # → Three
    menu.handle_key(menu.UP_KEY)  # → Two
    menu.handle_key(menu.UP_KEY)  # → One
    menu.handle_key(" ")  # uncheck One
    assert menu.checked == {3}
    assert menu.selected == 0

    # One should be visible again
    start, end = menu.visible_options_range
    assert start <= 0 < end


def test_enter_rejected_when_nothing_checked():
    """Enter in multi-select with nothing checked must fail and flag invalid."""
    menu = Menu("Pick", OPTIONS, multiple=True)
    assert menu.checked == set()

    # Validation should mark menu invalid
    menu.on_validate()
    assert menu.valid is False
    assert menu.validation_message == "Please select at least one option"

    # After checking one item, enter should succeed
    menu.handle_key(" ")
    assert menu.checked == {0}
    menu.on_validate()
    assert menu.valid is True


def test_enter_allowed_when_filter_yields_no_results_but_items_checked():
    """Enter in multi-select should succeed when items are checked, even if filter shows no results."""
    menu = Menu("Pick", OPTIONS, multiple=True, allow_filtering=True)

    # Check an item first
    menu.handle_key(" ")  # check Alpha
    assert menu.checked == {0}

    # Filter to something that yields no results
    menu.handle_key("x")
    menu.handle_key("y")
    menu.handle_key("z")
    assert len(menu.options) == 0  # no filtered results
    assert menu.checked == {0}  # but still have checked items

    # Validation should succeed because items are checked
    # Filter is just a navigation aid, not a submission constraint
    menu.on_validate()
    assert menu.valid is True
    assert menu.validation_message is None


def test_render_cancelled_single_select_menu():
    """Rendering a cancelled single-select menu should display 'Cancelled.' instead of crashing."""
    menu = Menu("Pick", OPTIONS)
    menu.selected = 1
    menu.on_cancel()

    result = _render_done_menu(menu)
    assert "Cancelled." in result.plain


def test_render_cancelled_multi_select_menu():
    """Rendering a cancelled multi-select menu should display 'Cancelled.' instead of crashing."""
    menu = Menu("Pick", OPTIONS, multiple=True)
    menu.checked = {0, 2}
    menu.on_cancel()

    result = _render_done_menu(menu)
    assert "Cancelled." in result.plain


def test_render_menu_with_invalid_selection_index():
    """Rendering a menu with out-of-bounds selection should display 'Cancelled.' instead of crashing."""
    menu = Menu("Pick", OPTIONS)
    menu.selected = 999

    result = _render_done_menu(menu)
    assert "Cancelled." in result.plain


def test_render_menu_with_negative_selection_index():
    """Rendering a menu with negative selection index should display 'Cancelled.' instead of crashing."""
    menu = Menu("Pick", OPTIONS)
    menu.selected = -1

    result = _render_done_menu(menu)
    assert "Cancelled." in result.plain


def test_render_normal_menu_still_works():
    """Ensure valid menu selections still render the selected option name."""
    menu = Menu("Pick", OPTIONS)
    menu.selected = 1

    result = _render_done_menu(menu)
    assert "Beta" in result.plain
    assert "Cancelled." not in result.plain


def test_render_multi_select_with_invalid_selection_shows_checked():
    """Multi-select menus should show checked items even with invalid selection index."""
    menu = Menu("Pick", OPTIONS, multiple=True)
    menu.checked = {0, 2}  # Alpha and Gamma checked
    menu.selected = 999  # Invalid selection, but shouldn't matter for multi-select

    result = _render_done_menu(menu)
    # Should show the checked items, not "Cancelled."
    assert "Alpha, Gamma" in result.plain
    assert "Cancelled." not in result.plain
