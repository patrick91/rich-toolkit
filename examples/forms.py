import rich

from rich_toolkit.form import Form
from rich_toolkit.styles import BorderedStyle, FancyStyle, MinimalStyle, TaggedStyle

for style in [
    FancyStyle(),
    MinimalStyle(),
    BorderedStyle(),
    TaggedStyle(tag_width=12),
]:
    form = Form(title="Enter your login details", style=style)

    form.add_button(name="ai", label="Fill with AI ✨", tag="form")  # TODO: callback?

    form.add_input(
        name="name", label="Name", placeholder="Enter your name", required=True
    )
    form.add_input(
        name="password",
        label="Password",
        placeholder="Enter your password",
        password=True,
        required=True,
    )

    form.add_button(name="submit", label="Submit")
    form.add_button(name="cancel", label="Cancel")

    results = form.run()

    print()
    rich.print(results)
    print()
