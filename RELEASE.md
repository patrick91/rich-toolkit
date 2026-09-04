---
release type: patch
---

This release handles interactive prompts cleanly when no controlling terminal is
available.

On Unix, failing to open `/dev/tty` now raises `EOFError` instead of exposing the
underlying operating-system error. Inputs and menus are marked as cancelled and
the final state is rendered before the error is propagated.
