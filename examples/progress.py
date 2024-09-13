import time

from rich_toolkit import RichToolkit, RichToolkitTheme
from rich_toolkit.styles import FancyStyle, TaggedStyle


for style in [TaggedStyle(tag_width=8), FancyStyle()]:
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
            "error": "red",
        },
    )

    with RichToolkit(theme=theme) as app:
        with app.progress("Some demo here") as progress:
            for x in range(3):
                time.sleep(0.1)
                progress.log(f"Step {x + 1} completed")

        app.print_line()

        with app.progress("Some demo here") as progress:
            time.sleep(0.3)

            progress.set_error("Something went wrong")

        app.print_line()

        with app.progress("Progress also support\nmultiple lines") as progress:
            time.sleep(2)

            progress.set_error("[error]Something went wrong\nbut on two lines")

        app.print_line()

        with app.progress("Progress can be hidden", transient=True) as progress:
            time.sleep(2)

        app.print("Done!", tag="result")

        with app.progress(
            "Progress can be hidden", transient=True, transient_on_error=False
        ) as progress:
            time.sleep(2)

            progress.set_error("Something went wrong")

    print("----------------------------------------")
