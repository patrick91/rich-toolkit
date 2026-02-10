---
release type: patch
---

Fixed cursor position when input labels wrap to multiple lines. Previously the
cursor offset was hardcoded assuming labels always take exactly one line, causing
the cursor to appear in the wrong position when labels were long enough to wrap.

Also fixed FancyStyle text being cut off at the terminal edge instead of wrapping
by accounting for the decoration prefix width when rendering content.
