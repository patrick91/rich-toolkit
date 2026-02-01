---
release type: patch
---

Fixed a crash that occurred when pressing Ctrl+C to cancel a menu. Previously, the `render_menu` function would crash with an `IndexError` when trying to display a cancelled menu because it attempted to access an invalid selection index.

The fix checks if the menu element was cancelled or has an invalid selection index before attempting to access the selected option, and displays "Cancelled." instead.

This also includes comprehensive test coverage for cancelled menu rendering scenarios.
