import time
from rich.theme import Theme
from rich_toolkit.input import Input

from rich.console import Console

from rich_toolkit.menu import Menu, Option
from rich_toolkit.progress import Progress


theme = Theme(
    {
        "tag.title": "black on #A7E3A2",
        "tag": "white on #893AE3",
        "placeholder": "grey85",
        "text": "white",
        "selected": "green",
        "result": "grey85",
        "progress": "on #893AE3",
    }
)
console = Console(theme=theme)

value = Input(console=console, title="Enter your name:").ask()

print(f"Hello, {value}!")

value_from_menu = Menu(
    console=console,
    title="Select your favorite color:",
    options=[
        Option({"value": "black", "name": "Black"}),
        Option({"value": "red", "name": "Red"}),
        Option({"value": "green", "name": "Green"}),
    ],
    allow_filtering=True,
).ask()

print(f"Your favorite color is {value_from_menu}!")


with Progress(console=console, title="Downloading...") as progress:
    for i in range(11):
        progress.log(f"Downloaded {i * 10}%")
        time.sleep(0.1)
