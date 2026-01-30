"""Basic usage demo for VHS recording."""

from rich_toolkit import RichToolkit
from rich_toolkit.styles.tagged import TaggedStyle

with RichToolkit(style=TaggedStyle()) as app:
    app.print_title("Launch sequence initiated.", tag="astro")
    name = app.input("What is your name?", tag="name")
    project_dir = app.input(
        "Where should we create your project?", tag="dir", default="./my-app"
    )
    if app.confirm("Continue?", tag="confirm"):
        app.print(f"Creating project for {name} in {project_dir}...")

    app.ask(
        label="Example",
        options=[
            {"value": True, "name": "Yes longer"},
            {"value": False, "name": "No longer"},
        ],
        inline=True,
    )
