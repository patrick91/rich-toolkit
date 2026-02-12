---
release type: patch
---

This release adds support for passing a `value` parameter to `Input` and `RichToolkit.input()`, which sets the initial editable text of the input field. The cursor is positioned at the end of the value, so users can immediately continue typing or edit the pre-populated text.

```python
app.input(
    "What is your name?",
    value="Patrick",
)
```
