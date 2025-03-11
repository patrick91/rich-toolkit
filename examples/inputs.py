from rich_toolkit import RichToolkit, RichToolkitTheme
from rich_toolkit.styles.border import BorderedStyle
from rich_toolkit.styles.fancy import FancyStyle
from rich_toolkit.styles.tagged import TaggedStyle

for style in [TaggedStyle(tag_width=12), BorderedStyle(), FancyStyle()]:
    theme = RichToolkitTheme(
        style=style,
        theme={
            "tag.title": "black on #A7E3A2",
            "tag": "white on #893AE3",
            "placeholder": "grey85",
            "text": "white",
            "selected": "green",
            "result": "grey85",
            "progress": "on #893AE3",
        },
    )

    with RichToolkit(theme=theme) as app:
        app.print_title("Launch sequence initiated.", tag="astro")

        app.print_line()

        app.input(
            "Where should we create your new project?",
            tag="dir",
            default="./some-app",
        )
        app.print_line()

        app.input("What is the name of your project?", tag="name")
        app.print_line()

        app.input("What's your password?", tag="password", password=True)
        app.print_line()

        app.input("Inline input:", tag="inline", inline=True)
        app.print_line()
        app.print("Done")
