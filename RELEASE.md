---
release type: patch
---

This release keeps updated progress titles visible when logs are preserved.

For progress displays with inline preserved logs, assigning to
`progress.title` now also updates the displayed message unless
`progress.current_message` was changed explicitly.
