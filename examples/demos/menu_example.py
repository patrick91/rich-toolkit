"""Menu example demo for VHS recording."""

from rich_toolkit import RichToolkit
from rich_toolkit.styles.tagged import TaggedStyle

with RichToolkit(style=TaggedStyle()) as app:
    app.print_title("Launch sequence initiated.", tag="astro")
    framework = app.ask(
        "Choose a framework:",
        tag="framework",
        options=[
            {"name": "React", "value": "react"},
            {"name": "Vue", "value": "vue"},
            {"name": "Svelte", "value": "svelte"},
            {"name": "Angular", "value": "angular"},
        ],
    )
    app.print(f"Selected: {framework}")
