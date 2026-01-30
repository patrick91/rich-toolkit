"""Confirmation demo for VHS recording."""

from rich_toolkit import RichToolkit
from rich_toolkit.styles.tagged import TaggedStyle

with RichToolkit(style=TaggedStyle()) as app:
    if app.confirm("Do you want to continue?", tag="confirm"):
        app.print("Continuing...")

    if app.confirm("Delete all files?", tag="confirm"):
        app.print("Deleting...")
    else:
        app.print("Cancelled.")
