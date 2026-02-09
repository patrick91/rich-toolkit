---
release type: minor
---

This release refactors our styling a bit, improving the visual distinction between submitted input values and placeholders, and properly handling the cancelled state of inputs.

In addition to that we also merge the custom theme on top of the base theme instead of replacing it, which allows us to preserve base styles like `placeholder.cancelled` while still allowing users to customize their themes.
