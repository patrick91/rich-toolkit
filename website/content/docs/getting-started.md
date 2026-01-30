# Getting Started

Rich Toolkit is an opinionated set of components for building beautiful CLI applications, built on top of [Rich](https://github.com/Textualize/rich).

## Installation

Install Rich Toolkit using pip:

```bash
pip install rich-toolkit
```

## Quick Start

The simplest way to use Rich Toolkit is with the `RichToolkit` class as a context manager:

```python
from rich_toolkit import RichToolkit

with RichToolkit() as app:
    app.print_title("Welcome to My CLI App!")
    app.print("Hello, world!")
```

## Basic Usage

Here's what a Rich Toolkit application looks like in action:

<TerminalExample example="basic_usage.py" height="200px" />

### Displaying Text

```python
from rich_toolkit import RichToolkit

with RichToolkit() as app:
    app.print_title("My Application", tag="app")
    app.print("This is a regular message")
    app.print_line()  # Print a separator line
```

### Getting User Input

```python
from rich_toolkit import RichToolkit

with RichToolkit() as app:
    # Simple text input
    name = app.input("What is your name?", tag="name")

    # Input with default value
    project_dir = app.input(
        "Where should we create your project?",
        tag="dir",
        default="./my-app"
    )

    # Password input (hidden)
    password = app.input(
        "Enter password:",
        tag="password",
        password=True
    )
```

**Example output:**

<TerminalExample example="input_types.py" height="150px" />

### Confirmation Prompts

```python
from rich_toolkit import RichToolkit

with RichToolkit() as app:
    if app.confirm("Do you want to continue?"):
        app.print("Continuing...")
    else:
        app.print("Cancelled.")
```

**Example output:**

<TerminalExample example="confirmation.py" height="120px" />

### Menus and Selection

```python
from rich_toolkit import RichToolkit

with RichToolkit() as app:
    # Simple menu
    framework = app.ask(
        "Choose a framework:",
        tag="framework",
        options=[
            {"name": "React", "value": "react"},
            {"name": "Vue", "value": "vue"},
            {"name": "Svelte", "value": "svelte"},
        ]
    )

    # Filterable menu (type to search)
    package = app.ask(
        "Select a package:",
        tag="pkg",
        options=[
            {"name": "requests", "value": "requests"},
            {"name": "fastapi", "value": "fastapi"},
            {"name": "django", "value": "django"},
        ],
        allow_filtering=True
    )
```

**Example output:**

<TerminalExample example="menu_example.py" height="200px" />

## Styling Your App

Rich Toolkit comes with several built-in styles to customize the appearance of your CLI:

### Tagged Style

```python
from rich_toolkit import RichToolkit
from rich_toolkit.styles.tagged import TaggedStyle

style = TaggedStyle(tag_width=12)

with RichToolkit(style=style) as app:
    app.print_title("Tagged Style Example", tag="demo")
    app.print("This uses tags on the left side")
```

### Bordered Style

```python
from rich_toolkit import RichToolkit
from rich_toolkit.styles.border import BorderedStyle

style = BorderedStyle()

with RichToolkit(style=style) as app:
    app.print_title("Bordered Style Example", tag="demo")
    app.print("This uses borders around content")
```

**Example output:**

<TerminalExample example="bordered_style.py" height="340px" />

### Fancy Style

```python
from rich_toolkit import RichToolkit
from rich_toolkit.styles.fancy import FancyStyle

style = FancyStyle()

with RichToolkit(style=style) as app:
    app.print_title("Fancy Style Example", tag="demo")
    app.print("This uses a more decorative style")
```

## Custom Themes

You can customize colors and appearance with themes:

```python
from rich_toolkit import RichToolkit, RichToolkitTheme
from rich_toolkit.styles.tagged import TaggedStyle

theme = RichToolkitTheme(
    style=TaggedStyle(tag_width=12),
    theme={
        "tag.title": "black on #A7E3A2",
        "tag": "white on #893AE3",
        "placeholder": "grey85",
        "text": "white",
        "selected": "green",
        "result": "grey85",
        "progress": "on #893AE3",
    }
)

with RichToolkit(theme=theme) as app:
    app.print_title("Custom Theme", tag="theme")
    app.print("Your themed application!")
```

## Next Steps

Now that you've learned the basics, explore more features:

- Check out the [examples directory](https://github.com/Textualize/rich-toolkit/tree/main/examples) for complete examples
- Learn about progress indicators and advanced components
- Customize your own styles and themes

Happy building!
