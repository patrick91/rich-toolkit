---
release type: patch
---

This release lets styles control the automatic context-manager padding printed
when entering and exiting `RichToolkit`.

`BaseStyle` now exposes `render_context_enter()` and `render_context_exit()`
hooks. Existing styled output keeps the previous blank padding by default, while
`MinimalStyle` suppresses both automatic lines so minimal applications do not
emit extra newlines around their content.
