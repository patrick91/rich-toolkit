import time
from typing import Any, Callable, List, Optional, Tuple

import click
import rich
from rich import box
from rich.console import Console, Group, RenderableType
from rich.control import Control, ControlType
from rich.live import Live
from rich.live_render import LiveRender

from rich.panel import Panel
from rich.padding import Padding
from rich.segment import Segment
from rich.text import Text
from rich.console import ConsoleOptions, RenderResult, Style
from rich_toolkit.plain_input import Input
from rich.cells import cell_len


# ┌ Name ──────────────────────────────────────────┐
# │ patr                                           │
# └────────────────────────────────────────────────┘
# ┌ Password ──────────────────────────────────────┐
# │                                                │
# └────────────────────────────────────────────────┘
# This field is required
#  ----- (see left padding, it's nice)
#  ┌ What is the name of your project? ───────────────────────────┐
#  │ E.g. example-app                                             │
#  └──────────────────────────────────────────────────────────────┘


class ToolkitPanel(Panel):
    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        # copied from Panel.__rich_console__
        _padding = Padding.unpack(self.padding)
        renderable = (
            Padding(self.renderable, _padding) if any(_padding) else self.renderable
        )
        style = console.get_style(self.style)
        partial_border_style = console.get_style(self.border_style)
        border_style = style + partial_border_style
        width = (
            options.max_width
            if self.width is None
            else min(options.max_width, self.width)
        )

        safe_box: bool = console.safe_box if self.safe_box is None else self.safe_box
        box = self.box.substitute(options, safe=safe_box)

        def align_text(
            text: Text, width: int, align: str, character: str, style: Style
        ) -> Text:
            """Gets new aligned text.

            Args:
                text (Text): Title or subtitle text.
                width (int): Desired width.
                align (str): Alignment.
                character (str): Character for alignment.
                style (Style): Border style

            Returns:
                Text: New text instance
            """
            text = text.copy()
            text.truncate(width)
            excess_space = width - cell_len(text.plain)
            if text.style:
                text.stylize(console.get_style(text.style))

            if excess_space:
                if align == "left":
                    return Text.assemble(
                        text,
                        (character * excess_space, style),
                        no_wrap=True,
                        end="",
                    )
                elif align == "center":
                    left = excess_space // 2
                    return Text.assemble(
                        (character * left, style),
                        text,
                        (character * (excess_space - left), style),
                        no_wrap=True,
                        end="",
                    )
                else:
                    return Text.assemble(
                        (character * excess_space, style),
                        text,
                        no_wrap=True,
                        end="",
                    )
            return text

        title_text = self._title
        if title_text is not None:
            title_text.stylize_before(partial_border_style)

        child_width = (
            width - 2
            if self.expand
            else console.measure(
                renderable, options=options.update_width(width - 2)
            ).maximum
        )
        child_height = self.height or options.height or None
        if child_height:
            child_height -= 2
        if title_text is not None:
            child_width = min(
                options.max_width - 2, max(child_width, title_text.cell_len + 2)
            )

        width = child_width + 2
        child_options = options.update(
            width=child_width, height=child_height, highlight=self.highlight
        )
        lines = console.render_lines(renderable, child_options, style=style)

        line_start = Segment(box.mid_left, border_style)
        line_end = Segment(f"{box.mid_right}", border_style)
        new_line = Segment.line()
        if title_text is None or width <= 4:
            yield Segment(box.get_top([width - 2]), border_style)
        else:
            title_text = align_text(
                title_text,
                width - 4,
                self.title_align,
                box.top,
                border_style,
            )
            # changed from box.top_left + box.top to box.top_left
            yield Segment(box.top_left, border_style)
            yield from console.render(title_text, child_options.update_width(width - 4))
            # changed from box.top + box.top_right to box.top * 2 + box.top_right
            yield Segment(box.top * 2 + box.top_right, border_style)

        yield new_line
        for line in lines:
            yield line_start
            yield from line
            yield line_end
            yield new_line

        subtitle_text = self._subtitle
        if subtitle_text is not None:
            subtitle_text.stylize_before(partial_border_style)

        if subtitle_text is None or width <= 4:
            yield Segment(box.get_bottom([width - 2]), border_style)
        else:
            subtitle_text = align_text(
                subtitle_text,
                width - 4,
                self.subtitle_align,
                box.bottom,
                border_style,
            )
            yield Segment(box.bottom_left + box.bottom, border_style)
            yield from console.render(
                subtitle_text, child_options.update_width(width - 4)
            )
            yield Segment(box.bottom + box.bottom_right, border_style)

        yield new_line


class Button:
    def __init__(self, name: str, label: str, callback: Optional[Callable] = None):
        self.name = name
        self.label = label
        self.callback = callback

    @property
    def should_show_cursor(self) -> bool:
        return False

    def render(self, is_active: bool = False) -> RenderableType:
        style = "black on blue" if is_active else "white on black"
        return Text(f" {self.label} ", style=style)

    def activate(self) -> Any:
        if self.callback:
            return self.callback()
        return True

    @property
    def size(self) -> Tuple[int, int]:
        return [0, 1]


class InputWithLabel:
    def __init__(
        self,
        name: str,
        label: str,
        placeholder: str,
        password: bool = False,
        inline: bool = False,
    ):
        self.name = name
        self.label = label
        self.placeholder = placeholder
        self.password = password
        self.inline = inline
        self.input = Input(console=Console(), password=password)

        self._input_position = None

        if inline:
            self.input._cursor_offset = len(self.label) + 1

        self._height = None

    def render(self, is_active: bool = False) -> RenderableType:
        label = self.label

        if is_active:
            label = f"[bold green]{label}[/bold green]"
        elif not self.input.valid:
            label = f"[bold red]{label}[/bold red]"

        contents = []

        if self.inline:
            contents.append(label + " " + self.input.render(is_active=is_active))
            self._input_position = 1
        else:
            contents.append(label)
            contents.append(self.input.render(is_active=is_active))
            self._input_position = 2

        if self.input.valid is False:
            contents.append(Text("This field is required", style="bold red"))

        self._height = len(contents)

        return Group(*contents)

    def on_blur(self):
        self.input.on_blur()

    @property
    def should_show_cursor(self) -> bool:
        return self.input.should_show_cursor

    @property
    def cursor_left(self) -> int:
        return self.input.cursor_left

    @property
    def text(self) -> str:
        return self.input.text

    @property
    def size(self) -> Tuple[int, int]:
        assert self._height is not None

        return [0, self._height]

    def update_text(self, text: str):
        self.input.update_text(text)


class StreamingContainer(Live):
    def __init__(self, container: "Container"):
        self.container = container
        self.container.title = "Streaming container"
        self.logs = []
        self.footer_content = ""
        super().__init__()

    def log(self, text: str):
        self.logs.append(text)

    def footer(self, text: str):
        self.footer_content = text

    def __enter__(self):
        self.start()

        return self

    def render(self, is_active: bool = False) -> RenderableType:
        return Group(
            *self.logs,
            self.footer_content,
        )

    @property
    def size(self) -> Tuple[int, int]:
        return [0, len(self.logs) + 1]

    def get_renderable(self) -> RenderableType:
        return self.container.style.decorate(self).content


class Container:
    def __init__(self, style: Any):
        self.elements: List[Input | Button] = []
        self.active_element_index = 0
        self.previous_element_index = 0
        self._live_render = LiveRender("")
        self.console = Console()
        self.style = style

    def _refresh(self, done: bool = False):
        self._live_render.set_renderable(self.render())

        active_element = self.elements[self.active_element_index]

        should_show_cursor = (
            active_element.should_show_cursor
            if hasattr(active_element, "should_show_cursor")
            else False
        )

        self.console.print(
            Control.show_cursor(should_show_cursor),
            *self.move_cursor_at_beginning(),
            self._live_render,
        )

        if not done:
            self.console.print(
                *self.move_cursor_to_active_element(),
            )

    @property
    def _active_element(self) -> "RenderWrapper":
        return self._content[self.active_element_index]

    def _get_element_position(self, element_index: int) -> int:
        position = 0

        for i in range(element_index + 1):
            current_element = self._content[i]

            if i == element_index:
                position += current_element.cursor_offset[0]
            else:
                position += current_element.size[1]

        return position

    @property
    def _active_element_position(self) -> int:
        return self._get_element_position(self.active_element_index)

    def get_offset_for_element(self, element_index: int) -> int:
        if self._live_render._shape is None:
            return 0

        position = self._get_element_position(element_index)

        _, height = self._live_render._shape

        return height - position

    def get_offset_for_active_element(self) -> int:
        return self.get_offset_for_element(self.active_element_index)

    def move_cursor_to_active_element(self) -> Tuple[Control, ...]:
        move_up = self.get_offset_for_active_element()

        move_cursor = (
            (Control((ControlType.CURSOR_UP, move_up)),) if move_up > 0 else ()
        )

        cursor_left = self._active_element.cursor_offset[1]

        return (Control.move_to_column(cursor_left), *move_cursor)

    def move_cursor_at_beginning(self) -> Tuple[Control, ...]:
        if self._live_render._shape is None:
            return (Control(),)

        original = (self._live_render.position_cursor(),)

        # Use the previous element type and index for cursor positioning
        move_down = self.get_offset_for_element(self.previous_element_index)

        if move_down == 0:
            return original

        return (
            Control(
                (ControlType.CURSOR_DOWN, move_down),
            ),
            *original,
        )

    def render(self) -> RenderableType:
        self._content = []

        # Render inputs
        for i, element in enumerate(self.elements):
            self._content.append(
                self.style.decorate(
                    element,
                    is_active=i == self.active_element_index,
                )
            )

        title = self.title

        if self._live_render._shape is not None:
            title += f" h: {self._live_render._shape[1]} offset: {self.get_offset_for_active_element()}"

        return Group(
            # Text(title, style="bold"),
            *[wrapper.content for wrapper in self._content],
            "\n",
        )

    def stream(self):
        return StreamingContainer(self)

    def run(self):
        self._refresh()

        while True:
            try:
                key = click.getchar()

                # Store the previous element state
                self.previous_element_index = self.active_element_index

                if key == "\x1b[Z":
                    if hasattr(self.elements[self.active_element_index], "on_blur"):
                        self.elements[self.active_element_index].on_blur()

                    self.active_element_index -= 1
                    if self.active_element_index < 0:
                        self.active_element_index = len(self.elements) - 1

                elif key == "\t":
                    if hasattr(self.elements[self.active_element_index], "on_blur"):
                        self.elements[self.active_element_index].on_blur()

                    self.active_element_index += 1
                    if self.active_element_index >= len(self.elements):
                        self.active_element_index = 0

                elif key == "\r":  # Enter key
                    break

                else:
                    active_element = self.elements[self.active_element_index]

                    if hasattr(active_element, "update_text"):
                        # TODO: this should be handle key
                        active_element.update_text(key)

                self._refresh()

            except KeyboardInterrupt:
                # TODO: this is somewhat broken
                self._refresh(done=True)
                exit()

        self._refresh(done=True)


class Form(Container):
    def __init__(self, title: str, style: Any):
        super().__init__(style)

        self.title = title

    def add_input(
        self,
        name: str,
        label: str,
        placeholder: str,
        password: bool = False,
        inline: bool = False,
    ):
        input = InputWithLabel(name, label, placeholder, password, inline)

        self.elements.append(input)

    def add_button(self, name: str, label: str, callback: Optional[Callable] = None):
        button = Button(name=name, label=label, callback=callback)
        self.elements.append(button)

    def run(self):
        super().run()

        return self._collect_data()

    def _collect_data(self) -> dict:
        return {
            input.name: input.text
            for input in self.elements
            if isinstance(input, InputWithLabel)
        }


class RenderWrapper:
    def __init__(
        self, content: Any, cursor_offset: tuple[int, int], size: tuple[int, int]
    ) -> None:
        self.content = content
        self.cursor_offset = cursor_offset
        self._size = size

    @property
    def size(self) -> tuple[int, int]:
        console = Console()
        # print(measure_renderables(console, console.options, [self.content]))
        return self._size


class BorderedStyle:
    def decorate(
        self,
        renderable: InputWithLabel | Any,
        is_active: bool = False,
    ) -> RenderableType:
        if isinstance(renderable, StreamingContainer):
            return RenderWrapper(
                Group(
                    ToolkitPanel.fit(
                        Group(*renderable.logs), title="LOL", title_align="left"
                    ),
                    renderable.footer_content,
                ),
                (0, 0),
                # TODO: how can we use rich to calculate the height?
                (50, 0),
            )

        if isinstance(renderable, InputWithLabel):
            # just to get some variables set
            renderable.render()

            if renderable.inline:
                box_width = 50

                content = f"─ {renderable.label}: {renderable.text} ─"

                cursor_left = len(renderable.label) + 4 + renderable.cursor_left
                cursor_top = 1

                return RenderWrapper(content, (cursor_top, cursor_left), (box_width, 1))
            else:
                if renderable.input.valid is False:
                    validation_message = (
                        Text("This field is required", style="bold red"),
                    )
                else:
                    validation_message = ()

                content = Group(
                    ToolkitPanel(
                        renderable.text,
                        highlight=is_active,
                        title=renderable.label,
                        title_align="left",
                        width=50,
                        box=box.SQUARE,
                    ),
                    *validation_message,
                )

                cursor_left = renderable.cursor_left + 2
                cursor_top = 2

                return RenderWrapper(
                    content,
                    (cursor_top, cursor_left),
                    (50, 3 + len(validation_message)),
                )

            # TODO: is this fine? the styles know how to render components?

        return RenderWrapper(
            renderable.render(is_active=is_active),
            (0, 0),
            (renderable.size[0], renderable.size[1]),
        )


class TaggedStyle:
    def __init__(self, tag: str, tag_width: int = 12):
        self.tag = tag
        self.tag_width = tag_width

    def _tag_element(self, child: RenderableType) -> Segment:
        left_padding = self.tag_width - len(self.tag)
        left_padding = max(0, left_padding)

        element = []

        element.append(Segment(" " * left_padding))
        element.append(Segment(self.tag))
        element.append(Segment(" " * left_padding))
        element.append(child)

        return element

    def decorate(
        self,
        renderable: InputWithLabel | Any,
        is_active: bool = False,
    ) -> RenderableType:
        rendered = renderable.render(is_active=is_active)

        if isinstance(rendered, Group):
            renderables = []

            for child in rendered._renderables:
                renderables.extend(self._tag_element(child))

            return RenderWrapper(Group(*renderables), (0, 0), (50, 3))

        return RenderWrapper(Group(*self._tag_element(rendered)), (0, 0), (50, 3))


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
        for x in range(10):
            stream.log(f"Hello {x}")
            stream.footer(f"Footer {x}")
            time.sleep(1)

    ...


for style in [BorderedStyle(), TaggedStyle("straw")]:
    print(f"Running with {style.__class__.__name__}")
    run_form(style)

    print()

    run_logs(style)
