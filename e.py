import time
from typing import Any

import rich

from rich_toolkit.container import Container
from rich_toolkit.form import Form
from rich_toolkit.input import Input
from rich_toolkit.styles.border import BorderedStyle
from rich_toolkit.styles.tagged import TaggedStyle


def run_input(style: Any):
    input = Input(
        name="name", label="Enter your name", placeholder="Patrick", style=style
    )

    print(input.ask())


def run_form(style: Any):
    # Example with multiple inputs and a button
    form = Form(title="Enter your login details", style=style)

    form.add_button(name="AI", label="AI")

    form.add_input(name="name", label="Name", placeholder="Enter your name")
    form.add_input(
        name="password",
        label="Password",
        placeholder="Enter your password",
        password=True,
    )

    # Add a submit button
    form.add_button(name="submit", label="Submit")
    form.add_input(
        name="email", label="Email", placeholder="Enter your email", inline=True
    )

    # Add a cancel button
    form.add_button(name="cancel", label="Cancel")

    results = form.run()

    print()
    rich.print(results)
    print()


def run_logs(style: Any):
    container = Container(style=style)

    with container.stream() as stream:
        for x in range(5):
            stream.log(f"Hello {x}")
            stream.footer(f"Footer {x}")
            time.sleep(0.5)


for style in [TaggedStyle("straw"), BorderedStyle()]:
    print(f"Running with {style.__class__.__name__}")

    run_input(style)

    print()

    run_form(style)

    print()

    run_logs(style)
