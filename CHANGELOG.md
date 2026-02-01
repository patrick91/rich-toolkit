CHANGELOG
=========

0.18.0 - 2026-02-01
-------------------

This release adds multiple selection support to the Menu component.

When passing `multiple=True` to `RichToolkit.ask()` or `Menu()`, the menu
switches to multi-select mode:

- Uses square characters (`■`/`□`) instead of circles (`●`/`○`)
- **Space** toggles the checked state of the current item
- **Arrow keys / j/k** move the cursor independently of checked state
- **Enter** confirms the selection (requires at least one checked item)
- Returns a list of selected values instead of a single value

```python
selected = app.ask(
    "Which languages do you use?",
    options=[
        {"name": "Python", "value": "python"},
        {"name": "JavaScript", "value": "javascript"},
        {"name": "Rust", "value": "rust"},
    ],
    multiple=True,
)
# selected is e.g. ["python", "rust"]
```

Works with filtering (`allow_filtering=True`) and all existing styles
(tagged, bordered, etc.). Raises `ValueError` if combined with `inline=True`.

This release was contributed by [@patrick91](https://github.com/patrick91) in [#46](https://github.com/patrick91/rich-toolkit/pull/46)

0.17.2 - 2026-01-29
-------------------

This release fixed the colour detection function, mostly to fix a bug 
interfering with forked worker processes (e.g. uvicorn with `--workers`).

The colour query now uses a dedicated file descriptor instead of stdin/stdout,
preventing issues with logging and signal handling in multi-process environments.

0.17.1 - 2025-12-17
-------------------

Fix inline menu option wrapping by using spaces instead of tabs.

When using inline menus (e.g., `app.confirm()`), options like "Yes" and "No" were wrapping to separate lines due to tab character separators expanding unpredictably in fixed-width table columns. This release replaces tab separators with two spaces for consistent, predictable spacing.

**Before:**
```
● Yes
○ No
```

**After:**
```
● Yes  ○ No
```

0.17.0 - 2025-11-27
-------------------

Add scrolling support for menus with many options.

When a menu has more options than can fit on the terminal screen, it now
automatically scrolls as the user navigates with arrow keys. This prevents
the UI from breaking when the terminal is too small to display all options.

Features:
- Automatic scrolling based on terminal height
- Scroll indicators (`↑ more` / `↓ more`) show when more options exist
- Works with both `TaggedStyle` and `BorderedStyle`
- Works with filterable menus (scroll resets when filter changes)
- Optional `max_visible` parameter for explicit control

Example usage:

```python
from rich_toolkit import RichToolkit
from rich_toolkit.styles.tagged import TaggedStyle

# Auto-scrolling based on terminal height
with RichToolkit(style=TaggedStyle()) as app:
    result = app.ask(
        "Select a country:",
        options=[{"name": country, "value": country} for country in countries],
        allow_filtering=True,
    )

# Or with explicit max_visible limit
from rich_toolkit.menu import Menu

menu = Menu(
    label="Pick an option:",
    options=[{"name": f"Option {i}", "value": i} for i in range(50)],
    max_visible=10,  # Only show 10 options at a time
)
result = menu.ask()
```

0.16.0 - 2025-11-19
-------------------

Add Pydantic v1/v2 compatibility for Input validators using a Protocol-based approach.

The `Input` component now accepts any object with a `validate_python` method through the new `Validator` protocol, making it compatible with both Pydantic v1 and v2.

**Usage with Pydantic v2:**
```python
from pydantic import TypeAdapter

validator = TypeAdapter(int)
app.input("Enter a number:", validator=validator)
```

**Usage with Pydantic v1:**
```python
from pydantic import parse_obj_as

class V1Validator:
    def __init__(self, type_):
        self.type_ = type_

    def validate_python(self, value):
        return parse_obj_as(self.type_, value)

validator = V1Validator(int)
app.input("Enter a number:", validator=validator)
```

**Changes:**
- Added `Validator` protocol that accepts any object with a `validate_python` method
- Improved error message extraction from Pydantic validation errors
- Added cross-version compatibility tests
- Updated CI to test both Pydantic v1 and v2 across Python 3.8-3.14

0.15.1 - 2025-09-04
-------------------

This release add proper support for CJK characters

0.15.0 - 2025-08-11
-------------------

This release increases the paste buffer from 32 to 4096 characters, enabling users to paste longer text into input fields.

It also adds full Windows compatibility with proper special key handling and fixes how password fields to always show asterisks.