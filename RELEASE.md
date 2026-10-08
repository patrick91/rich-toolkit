---
release type: patch
---

`confirm()` now honours `default`: `confirm("Delete?", default=False)` starts
on "No", so pressing Enter returns `False`. Previously `default` was ignored and
Enter always returned `True`. `confirm()` still defaults to "Yes".

`ask()` and `Menu` accept `default` too, which starts on the option with that
value instead of the first one.
