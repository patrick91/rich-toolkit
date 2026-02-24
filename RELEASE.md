---
release type: patch
---

Fix metadata being lost when passed to `Progress`. `Element.__init__` was called
without the `metadata` argument, causing it to be overwritten to an empty dict.
Also removed a redundant `self.metadata` assignment in `Menu`.
