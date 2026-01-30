"""Input types demo for VHS recording."""

from rich_toolkit import RichToolkit
from rich_toolkit.styles.tagged import TaggedStyle

with RichToolkit(style=TaggedStyle()) as app:
    email = app.input("Enter your email:", tag="email")
    password = app.input("Enter password:", tag="password", password=True)
    port = app.input("Port number:", tag="port")
    app.print("Configuration saved!")
