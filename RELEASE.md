---
release type: patch
---

This release fixed the colour detection function, mostly to fix a bug 
interfering with forked worker processes (e.g. uvicorn with `--workers`).

The colour query now uses a dedicated file descriptor instead of stdin/stdout,
preventing issues with logging and signal handling in multi-process environments.
