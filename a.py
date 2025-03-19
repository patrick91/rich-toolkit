from rich_toolkit.styles.tagged import TaggedStyle

from rich_toolkit import RichToolkit

with RichToolkit(style=TaggedStyle(theme={"tag": "red"})) as app:
    app.print("Hello, World!", "🍓")
