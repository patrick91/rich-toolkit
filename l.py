import rich
from rich.table import Column, Table
from rich.box import SIMPLE


width = 10
table = Table(
    Column(width=width),
    padding=(0, 1, 0, 0),
    show_header=False,
    box=SIMPLE,
)

tag = "astro"
left_padding = width - len(tag) - 2

tag = " " * left_padding + "[on red] " + tag + " [/on red]"

table.add_row(tag, "What's the name of the app?")
table.add_row("", "Something cool")
table.add_row("", "")
table.add_row("", "Something\non two lines")

rich.print(table)