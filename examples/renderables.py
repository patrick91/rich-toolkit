from rich.tree import Tree
from rich_toolkit.toolkit import RichToolkit
from rich_toolkit.styles import BorderedStyle, FancyStyle, TaggedStyle

theme = {
    "tag.title": "black on #A7E3A2",
    "tag": "white on #893AE3",
    "placeholder": "grey85",
    "text": "white",
    "selected": "green",
    "result": "grey85",
    "progress": "on #893AE3",
}

for style in [
    BorderedStyle(theme=theme),
    FancyStyle(theme=theme),
    TaggedStyle(theme=theme),
]:
    with RichToolkit(style=style) as app:
        tree = Tree("root")
        tree.add("child")

        app.print(tree, "Hello, World!")
