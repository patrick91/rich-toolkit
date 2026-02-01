from rich_toolkit import RichToolkit
from rich_toolkit.styles.border import BorderedStyle
from rich_toolkit.styles.tagged import TaggedStyle


theme = {
    "tag.title": "black on #A7E3A2",
    "tag": "white on #893AE3",
    "placeholder": "grey85",
    "text": "white",
    "selected": "green",
    "result": "grey85",
    "progress": "on #893AE3",
}

options = [
    {"name": "Python", "value": "python"},
    {"name": "JavaScript", "value": "javascript"},
    {"name": "TypeScript", "value": "typescript"},
    {"name": "Rust", "value": "rust"},
    {"name": "Go", "value": "go"},
]

for style in [TaggedStyle(tag_width=12, theme=theme), BorderedStyle(theme=theme)]:
    print("Style: ", style)
    print()
    with RichToolkit(style=style) as app:
        app.print_title("Multi-select demo", tag="demo")
        app.print_line()

        selected = app.ask(
            "Which languages do you use?",
            tag="langs",
            options=options,
            multiple=True,
        )
        app.print_line()

        app.print(f"You selected: {', '.join(selected)}")
        app.print_line()

        selected_with_filter = app.ask(
            "Pick languages again (with filtering)",
            tag="langs",
            options=options,
            multiple=True,
            allow_filtering=True,
        )
        app.print_line()

        app.print(f"You selected: {', '.join(selected_with_filter)}")
        app.print_line()
