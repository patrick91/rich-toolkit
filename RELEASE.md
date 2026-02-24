---
release type: patch
---

Show cancelled state when progress is interrupted with Ctrl+C.

Previously, pressing Ctrl+C during a progress operation would exit without
any visual indication that the operation was cancelled. Now, the progress
displays "Cancelled." (matching how inputs and menus already handle cancellation).

The tagged style also shows the tag blocks in red (using error animation colors)
when a progress is cancelled.
