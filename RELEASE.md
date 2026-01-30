---
release type: minor
---

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
