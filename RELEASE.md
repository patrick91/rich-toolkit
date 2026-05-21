---
release type: patch
---

This release fixes the terminal color query hanging when the program runs from
a background process group.

`_get_terminal_color` used `tty.setcbreak`, which calls `tcsetattr` and
generates `SIGTTOU` when invoked from a background process group (for example
when the program is launched with `prog &` or run under a job-control shell
that isn't giving it the terminal). The default disposition of `SIGTTOU` stops
the process, so the program would hang.

It now checks that it owns the terminal's foreground process group before
querying, and falls back to the default color otherwise.
