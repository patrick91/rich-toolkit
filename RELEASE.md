---
release type: minor
---

Improved input value styling and cancelled state handling:

- Submitted input values now use the `result` style instead of `placeholder`/`text`,
  making them visually distinct from placeholders.
- Cancelled inputs with typed text now properly show the `placeholder.cancelled` style.
- Cancelled state takes priority over done state, fixing the case where
  KeyboardInterrupt would show result styling instead of cancelled styling.
- `RichToolkitTheme` now merges custom themes on top of the base theme instead of
  replacing it, preserving base styles like `placeholder.cancelled`.
- Added italic to the `cancelled` theme style and a blank line before validation messages.
