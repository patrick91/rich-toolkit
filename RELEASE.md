---
release type: patch
---

This release preserves progress logs automatically in CI and non-interactive
output.

In these environments, every `progress.log()` message appears in the output once
without line breaks inserted at the terminal width. Interactive terminals
continue to use the live progress display.

Pass `preserve_progress_logs=True` or `preserve_progress_logs=False` to
`RichToolkit` to override the behavior globally. Individual progress displays
can override it with `preserve_logs`.
