---
release type: patch
---

This release adds support for passing `end` to `RichToolkit.print()`,
`RichToolkit.print_title()`, and `Progress.log()`.

This makes it possible to print or log partial lines without automatically
ending them with a newline:

```python
app.print("Hello, ", end="")
app.print("World!")

with app.progress("Downloading") as progress:
    progress.log("Downloaded ", end="")
    progress.log("50%")
```
