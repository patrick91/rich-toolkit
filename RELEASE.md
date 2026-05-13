---
release type: patch
---

This release fixes progress log rendering when messages contain embedded
newlines.

`Progress.log()` now preserves multiline messages in non-inline progress
rendering, while inline progress logs split embedded newlines into separate log
entries. This keeps partial-line logging with `end=""` working while also
handling output that arrives with newline characters already included.

Cancelled progress rendering now keeps the progress output that was already
visible and always shows `Cancelled.` on its own final line, avoiding duplicated
titles in framed styles.
