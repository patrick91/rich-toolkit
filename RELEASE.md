---
release type: minor
---

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
