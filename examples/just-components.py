import time

from rich_toolkit.input import Input
from rich_toolkit.menu import Menu, Option
from rich_toolkit.progress import Progress

with Progress(title="Downloading...") as progress:
    for i in range(11):
        progress.log(f"Downloaded {i * 10}%")
        time.sleep(0.1)

with Progress(title="Downloading (inline logs)...", inline_logs=True) as progress:
    for i in range(11):
        progress.log(f"Downloaded {i * 10}%")
        time.sleep(0.1)

value = Input("Enter your name:", name="name", default="John").ask()

print(f"Hello, {value}!")

value = Input("Enter your name (inline):", inline=True, required=True).ask()

print(f"Hello, {value}!")

value_from_menu = Menu(
    label="Select your favorite color:",
    options=[
        Option({"value": "black", "name": "Black"}),
        Option({"value": "red", "name": "Red"}),
        Option({"value": "green", "name": "Green"}),
    ],
    allow_filtering=True,
).ask()

print(f"Your favorite color is {value_from_menu}!")
