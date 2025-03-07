from typing import Any, List, Tuple

import click
from rich.console import (
    Console,
    Group,
    RenderableType,
)
from rich.control import Control, ControlType
from rich.segment import Segment
from rich.live_render import LiveRender

from .element import Element


class Container:
    def __init__(self, style: Any):
        self.elements: List[Element] = []
        self.active_element_index = 0
        self.previous_element_index = 0
        self._live_render = LiveRender("")
        self.console = Console()
        self.style = style

    def _refresh(self, done: bool = False):
        self._live_render.set_renderable(self.render(done=done))

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
    def _active_element(self) -> Element:
        return self.elements[self.active_element_index]

    def _get_size(self, renderable: RenderableType) -> tuple[int, int]:
        lines = self.console.render_lines(renderable, self.console.options, pad=False)

        return Segment.get_shape(lines)

    def _get_element_position(self, element_index: int) -> int:
        position = 0

        for i in range(element_index + 1):
            current_element = self._content[i]

            if i == element_index:
                # TODO: we need to figure out this (maybe another call to style?)
                # position += current_element.cursor_offset.top
                position += self.style.get_cursor_offset_for_element(
                    self.elements[i]
                ).top
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

        cursor_left = self.style.get_cursor_offset_for_element(self._active_element).left

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

    def render(self, done: bool = False) -> RenderableType:
        self._content = []

        for i, element in enumerate(self.elements):
            self._content.append(
                self.style.decorate(
                    element,
                    is_active=i == self.active_element_index,
                )
            )

        return Group(
            *[wrapper for wrapper in self._content],
            "\n" if not done else "",
        )

    def stream(self):
        from .streaming_container import StreamingContainer

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
                # TODO: send a message to all elements that the user cancelled
                self._refresh(done=True)
                exit()

        self._refresh(done=True)
