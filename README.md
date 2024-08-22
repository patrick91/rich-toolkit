# Rich Toolkit

This is a very opinionated set of components for building CLI applications.
It is based on [Rich](https://github.com/Textualize/rich)

## Installation

```bash
pip install rich-toolkit
```

## Example usage

Rich toolkit comes with an `App` class, this is used to give a consistent
style to your CLI application, it can be used as a context manager, like so:

```python
from rich_toolkit import App

with App(base_color="#bada55") as app:
    app.print_title("Hello, World!", tag="MyApp")
```
