#!/usr/bin/env python3
"""
Build examples as HTML for documentation.

This script runs Rich Toolkit examples with mocked user inputs and captures
their actual output as HTML. The generated HTML files are embedded in the
documentation to show users what the output looks like.

Usage:
    uv run python scripts/build_examples.py

The script will generate HTML files in website/content/examples/ which
can be referenced in markdown documentation:

    <TerminalExample example="basic_usage.py" height="200px" />
"""

import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

# Add the src directory to the path so we can import rich_toolkit
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "src"))

from rich_toolkit._input_handler import TextInputHandler


# Example fixtures - define the keyboard inputs for each example
EXAMPLE_FIXTURES = {
    "basic_usage": {
        "steps": [
            *"John",  # Type name
            TextInputHandler.ENTER_KEY,
            TextInputHandler.ENTER_KEY,  # Accept default directory
            "y",  # Confirm
            TextInputHandler.ENTER_KEY,
        ],
        "source": """
from rich_toolkit import RichToolkit
from rich_toolkit.styles.tagged import TaggedStyle

with RichToolkit(style=TaggedStyle()) as app:
    app.print_title("Launch sequence initiated.", tag="astro")
    name = app.input("What is your name?", tag="name")
    project_dir = app.input(
        "Where should we create your project?",
        tag="dir",
        default="./my-app"
    )
    if app.confirm("Continue?", tag="confirm"):
        pass
""",
    },
    "input_types": {
        "steps": [
            *"user@example.com",
            TextInputHandler.ENTER_KEY,
            *"password123",
            TextInputHandler.ENTER_KEY,
            *"8080",
            TextInputHandler.ENTER_KEY,
        ],
        "source": """
from rich_toolkit import RichToolkit
from rich_toolkit.styles.tagged import TaggedStyle

with RichToolkit(style=TaggedStyle()) as app:
    app.input("Enter your email:", tag="email")
    app.input("Enter password:", tag="password", password=True)
    app.input("Port number:", tag="port")
""",
    },
    "confirmation": {
        "steps": [
            "y",
            TextInputHandler.ENTER_KEY,
            "n",
            TextInputHandler.ENTER_KEY,
        ],
        "source": """
from rich_toolkit import RichToolkit
from rich_toolkit.styles.tagged import TaggedStyle

with RichToolkit(style=TaggedStyle()) as app:
    app.confirm("Do you want to continue?", tag="confirm")
    app.confirm("Delete all files?", tag="confirm")
""",
    },
    "menu_example": {
        "steps": [
            TextInputHandler.DOWN_KEY,  # Navigate down
            TextInputHandler.ENTER_KEY,  # Select React
        ],
        "source": """
from rich_toolkit import RichToolkit
from rich_toolkit.styles.tagged import TaggedStyle

with RichToolkit(style=TaggedStyle()) as app:
    app.print_title("Launch sequence initiated.", tag="astro")
    app.ask(
        "Choose a framework:",
        tag="framework",
        options=[
            {"name": "React", "value": "react"},
            {"name": "Vue", "value": "vue"},
            {"name": "Svelte", "value": "svelte"},
            {"name": "Angular", "value": "angular"},
        ]
    )
""",
    },
    "bordered_style": {
        "steps": [
            *"John",
            TextInputHandler.ENTER_KEY,
            TextInputHandler.ENTER_KEY,  # Accept default
        ],
        "source": """
from rich_toolkit import RichToolkit
from rich_toolkit.styles.border import BorderedStyle

style = BorderedStyle()

with RichToolkit(style=style) as app:
    app.print_title("Launch sequence initiated.", tag="astro")
    app.input("What is your name?", tag="name")
    app.input("Where should we create your project?", tag="dir", default="./my-app")
""",
    },
}


def run_example_with_mocked_input(source_code: str, steps: list[Any]) -> str:
    """
    Run example code with mocked keyboard input and capture HTML output.

    Args:
        source_code: The Python code to execute
        steps: List of keyboard inputs (characters, ENTER_KEY, DOWN_KEY, etc.)

    Returns:
        HTML representation of the terminal output
    """
    from rich.console import Console

    # Create a console that records output
    console = Console(
        record=True,
        width=80,
        force_terminal=True,
        legacy_windows=False,
    )

    # Create an iterator from the steps
    steps_iter = iter(steps)

    def mock_getchar():
        """Mock getchar to return the next step."""
        try:
            return next(steps_iter)
        except StopIteration:
            # If we run out of steps, raise KeyboardInterrupt to exit
            raise KeyboardInterrupt()

    # Instead of trying to share consoles, let's capture all console output
    # We'll collect all print calls
    all_consoles = []

    from rich_toolkit.styles.base import BaseStyle

    original_base_init = BaseStyle.__init__

    def mock_base_style_init(self, *args, **kwargs):
        """Patch BaseStyle.__init__ to track console instances."""
        # Call the original init
        original_base_init(self, *args, **kwargs)
        # Make the console record output
        self.console._record = True
        self.console._record_buffer = []
        # Track this console
        all_consoles.append(self.console)

    # Patch getchar and BaseStyle console creation
    patches = [
        patch("rich_toolkit.container.getchar", side_effect=mock_getchar),
        patch("rich_toolkit._getchar.getchar", side_effect=mock_getchar),
        patch.object(BaseStyle, "__init__", mock_base_style_init),
    ]

    # Execute in a namespace with the console
    namespace = {
        "__name__": "__main__",
        "__builtins__": __builtins__,
    }

    # Apply all patches
    with patches[0], patches[1], patches[2]:
        try:
            exec(source_code, namespace)
        except KeyboardInterrupt:
            # Expected when we run out of steps
            pass
        except Exception as e:
            print(f"Error running example: {e}")
            import traceback

            traceback.print_exc()
            return ""

    # Export to HTML from the console that was actually used
    if all_consoles:
        html_content = all_consoles[0].export_html(
            inline_styles=True, code_format="<pre>{code}</pre>"
        )
    else:
        # Fallback to our recording console
        html_content = console.export_html(
            inline_styles=True, code_format="<pre>{code}</pre>"
        )

    # Wrap in a styled container
    wrapped_html = f"""<div class="rich-toolkit-example" style="background-color: #1e1e1e; border-radius: 8px; padding: 20px; margin: 20px 0; font-family: 'Menlo', 'Monaco', 'Courier New', monospace; overflow-x: auto;">
{html_content}
</div>"""

    return wrapped_html


def build_example(name: str, fixture: dict, output_dir: Path) -> str:
    """Build a single example and save it as HTML."""
    output_file = output_dir / f"{name}.html"

    print(f"Building {name}...")

    html = run_example_with_mocked_input(
        source_code=fixture["source"], steps=fixture["steps"]
    )

    if not html:
        print(f"  ⚠️  Failed to generate HTML for {name}")
        return ""

    with open(output_file, "w") as f:
        f.write(html)

    print(f"  ✓ Created {output_file}")
    return str(output_file)


def build_all_examples():
    """Build all example files."""
    output_dir = root_dir / "website" / "content" / "examples"
    output_dir.mkdir(exist_ok=True, parents=True)

    print("Building examples with mocked inputs")
    print(f"Output directory: {output_dir}")
    print()

    success_count = 0
    for name, fixture in EXAMPLE_FIXTURES.items():
        result = build_example(name, fixture, output_dir)
        if result:
            success_count += 1

    print()
    print(f"✓ Built {success_count}/{len(EXAMPLE_FIXTURES)} examples successfully")


if __name__ == "__main__":
    build_all_examples()
