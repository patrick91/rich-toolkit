from rich.theme import Theme
from rich_toolkit.input import Input

from rich.console import Console


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
