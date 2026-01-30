"""Bordered style demo for VHS recording."""

from rich_toolkit import RichToolkit
from rich_toolkit.styles.border import BorderedStyle

style = BorderedStyle()

with RichToolkit(style=style) as app:
    app.print_title("Launch sequence initiated.", tag="astro")
    name = app.input("What is your name?", tag="name")
    project_dir = app.input(
        "Where should we create your project?", tag="dir", default="./my-app"
    )
    app.print(f"Welcome, {name}!")
