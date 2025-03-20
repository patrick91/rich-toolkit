import random
import time

from rich_toolkit import RichToolkit
from rich_toolkit.styles.border import BorderedStyle

LOGO = r""" _                               _
| |                             | |
| |     __ _ _ __ __ ___   _____| |
| |    / _` |  __/ _` \ \ / / _ \ |
| |___| (_| | | | (_| |\ V /  __/ |
|______\__,_|_|  \__,_| \_/ \___|_|
"""


with RichToolkit(style=BorderedStyle(theme={"error": "bright_yellow"})) as app:
    app.print_title(f"[red]{LOGO}[/red]")

    app.print_line()

    app_name = app.input(
        "What is the name of your project?",
        placeholder="E.g. example-app",
        required=True,
        required_message="⚠ The project name is required.",
    )

    app.print_line()

    integration = app.ask(
        "Which starter kit would you like to install?",
        options=[
            {"name": "None", "value": "none"},
            {"name": "React", "value": "react"},
            {"name": "Vue", "value": "vue"},
            {"name": "Livewire", "value": "livewire"},
        ],
    )

    app.print_line()

    with app.progress("Downloading template...") as progress:
        for _ in range(10):
            time.sleep(random.uniform(0.05, 0.35))

    app.print_line()

    app.print("Done!")
