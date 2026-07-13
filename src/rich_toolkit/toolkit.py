from __future__ import annotations

import inspect
import json
import os
import sys
from collections.abc import Iterator
from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    TypeVar,
    Union,
    cast,
    overload,
)

from rich.console import ConsoleRenderable, RenderableType
from rich.pretty import Pretty
from rich.text import Text
from rich.theme import Theme
from typing_extensions import Concatenate, ParamSpec

from .input import Input
from .menu import Menu, Option, ReturnValue
from .progress import Progress
from .styles.base import BaseStyle

OutputT = TypeVar("OutputT")
ReturnT = TypeVar("ReturnT")
P = ParamSpec("P")
OutputRenderer = Union[
    Callable[[OutputT], Optional[RenderableType]],
    Callable[[OutputT, "RichToolkit"], Optional[RenderableType]],
]


def _unavailable_in_json_mode(
    method_name: str,
) -> Callable[
    [Callable[Concatenate["RichToolkit", P], ReturnT]],
    Callable[Concatenate["RichToolkit", P], ReturnT],
]:
    def decorator(
        method: Callable[Concatenate["RichToolkit", P], ReturnT],
    ) -> Callable[Concatenate["RichToolkit", P], ReturnT]:
        @wraps(method)
        def wrapper(self: "RichToolkit", *args: P.args, **kwargs: P.kwargs) -> ReturnT:
            if self.mode == "json":
                raise RuntimeError(f"{method_name}() is not available in JSON mode")

            return method(self, *args, **kwargs)

        return wrapper

    return decorator


def _is_output_stream(data: Any) -> bool:
    return isinstance(data, Iterator)


def _is_ci_enabled() -> bool:
    value = os.environ.get("CI")

    if value is None:
        return False

    return value.lower() not in {"", "0", "false", "no", "off"}


def _dump_output_data(data: Any) -> Any:
    model_dump = getattr(data, "model_dump", None)
    if callable(model_dump):
        return _dump_output_data(model_dump(mode="json"))

    if isinstance(data, dict):
        return {key: _dump_output_data(value) for key, value in data.items()}

    if isinstance(data, (list, tuple)):
        return [_dump_output_data(item) for item in data]

    return data


def _format_output_value(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, allow_nan=False)

    return str(value)


def _record_lines(data: dict[Any, Any]) -> list[str]:
    return [f"{key}: {_format_output_value(value)}" for key, value in data.items()]


def _default_output_renderable(data: Any) -> RenderableType:
    dumped = _dump_output_data(data)

    if isinstance(dumped, dict):
        return Text("\n".join(_record_lines(dumped)))

    if isinstance(dumped, list):
        lines: list[str] = []
        for index, item in enumerate(dumped):
            if not isinstance(item, dict):
                return Pretty(dumped)
            if index:
                lines.append("")
            lines.extend(_record_lines(item))
        return Text("\n".join(lines))

    return Pretty(dumped)


class RichToolkitTheme:
    def __init__(self, style: BaseStyle, theme: Dict[str, str]) -> None:
        self.style = style
        self.rich_theme = Theme(theme)


class RichToolkit:
    def __init__(
        self,
        style: Optional[BaseStyle] = None,
        theme: Optional[RichToolkitTheme] = None,
        handle_keyboard_interrupts: bool = True,
        mode: Literal["human", "json"] = "human",
        preserve_progress_logs: Optional[bool] = None,
    ) -> None:
        """Create a toolkit.

        Args:
            style: Style used to render toolkit elements.
            theme: Legacy theme configuration.
            handle_keyboard_interrupts: Suppress keyboard interrupts when enabled.
            mode: Render human-readable or JSON output.
            preserve_progress_logs: Print each progress log message immediately
                without inserting line breaks at the console width. When `None`,
                this is enabled in CI and for non-interactive consoles.
        """
        if mode not in ("human", "json"):
            raise ValueError("mode must be 'human' or 'json'")

        self.mode = mode
        self._json_output_written = False

        self.theme = theme
        if theme is not None:
            # TODO: deprecate
            self.style = theme.style
            self.style.theme = theme.rich_theme
            self.style.console.push_theme(theme.rich_theme)
        else:
            if style is None:
                from .styles import MinimalStyle

                style = MinimalStyle()

            self.style = style

        self.console = self.style.console
        if preserve_progress_logs is None:
            preserve_progress_logs = _is_ci_enabled() or not self.console.is_terminal
        self.preserve_progress_logs = preserve_progress_logs

        self.handle_keyboard_interrupts = handle_keyboard_interrupts

    def __enter__(self):
        if self.mode == "human":
            if (renderable := self.style.render_context_enter()) is not None:
                self.console.print(renderable)
        return self

    def __exit__(
        self, exc_type: Any, exc_value: Any, traceback: Any
    ) -> Union[bool, None]:
        if self.handle_keyboard_interrupts and exc_type is KeyboardInterrupt:
            # we want to handle keyboard interrupts gracefully, instead of showing a traceback
            # or any other error message
            return True

        if self.mode == "human":
            if (renderable := self.style.render_context_exit()) is not None:
                self.console.print(renderable)

        return None

    def print_title(self, title: str, end: str = "\n", **metadata: Any) -> None:
        if self.mode == "json":
            return

        self.console.print(
            self.style.render_element(title, title=True, **metadata), end=end
        )

    def _print(
        self,
        *renderables: RenderableType,
        end: str = "\n",
        _force: bool = False,
        **metadata: Any,
    ) -> None:
        if self.mode == "json" and not _force:
            return

        self.console.print(
            *[
                self.style.render_element(renderable, **metadata)
                for renderable in renderables
            ],
            end=end,
        )

    def print(
        self, *renderables: RenderableType, end: str = "\n", **metadata: Any
    ) -> None:
        self._print(*renderables, end=end, _force=False, **metadata)

    def print_as_string(self, *renderables: RenderableType, **metadata: Any) -> str:
        with self.console.capture() as capture:
            self._print(*renderables, _force=True, **metadata)

        return capture.get().rstrip()

    def print_line(self) -> None:
        if self.mode == "json":
            return

        self.console.print(self.style.empty_line())

    def _write_json_line(self, data: Any) -> None:
        payload = json.dumps(
            _dump_output_data(data),
            ensure_ascii=False,
            allow_nan=False,
        )
        sys.stdout.write(payload + "\n")
        sys.stdout.flush()

    def _render_custom_output(
        self, render_output: OutputRenderer[Any], data: Any
    ) -> None:
        signature = inspect.signature(render_output)

        if len(signature.parameters) == 1:
            render_one_arg = cast(
                Callable[[Any], Optional[RenderableType]],
                render_output,
            )
            renderable = render_one_arg(data)
        else:
            render_two_args = cast(
                Callable[[Any, RichToolkit], Optional[RenderableType]],
                render_output,
            )
            renderable = render_two_args(data, self)

        if renderable is not None:
            self.print(renderable)

    def _write_json_output(self, data: Any) -> None:
        if _is_output_stream(data):
            for item in data:
                self._write_json_line(item)
            return

        self._write_json_line(data)

    def _render_human_output(
        self,
        data: Any,
        render_output: Optional[Union[RenderableType, OutputRenderer[Any]]] = None,
    ) -> None:
        if render_output is not None:
            if callable(render_output):
                self._render_custom_output(
                    cast(OutputRenderer[Any], render_output), data
                )
            else:
                self.print(render_output)

            return

        if isinstance(data, (str, ConsoleRenderable)):
            self.print(data)
        else:
            self.print(_default_output_renderable(data))

    @overload
    def output(self, data: OutputT, render_output: None = None) -> None: ...

    @overload
    def output(self, data: OutputT, render_output: OutputRenderer[OutputT]) -> None: ...

    @overload
    def output(self, data: Any, render_output: RenderableType) -> None: ...

    def output(
        self,
        data: Any,
        render_output: Optional[Union[RenderableType, OutputRenderer[Any]]] = None,
    ) -> None:
        if self.mode == "json":
            if self._json_output_written:
                raise RuntimeError("output() was already called in JSON mode")

            self._write_json_output(data)
            self._json_output_written = True
            return

        if _is_output_stream(data):
            for item in data:
                self._render_human_output(item, render_output=render_output)
            return

        self._render_human_output(data, render_output=render_output)

    @_unavailable_in_json_mode("confirm")
    def confirm(self, label: str, **metadata: Any) -> bool:
        options: List[Option[bool]] = [
            Option({"value": True, "name": "Yes"}),
            Option({"value": False, "name": "No"}),
        ]

        return self.ask(
            label=label,
            options=options,
            inline=True,
            **metadata,
        )

    @overload
    def ask(
        self,
        label: str,
        options: List[Option[ReturnValue]],
        inline: bool = False,
        allow_filtering: bool = False,
        multiple: Literal[False] = False,
        **metadata: Any,
    ) -> ReturnValue: ...

    @overload
    def ask(
        self,
        label: str,
        options: List[Option[ReturnValue]],
        inline: bool = False,
        allow_filtering: bool = False,
        *,
        multiple: Literal[True],
        **metadata: Any,
    ) -> List[ReturnValue]: ...

    def ask(
        self,
        label: str,
        options: List[Option[ReturnValue]],
        inline: bool = False,
        allow_filtering: bool = False,
        multiple: bool = False,
        **metadata: Any,
    ) -> Union[ReturnValue, List[ReturnValue]]:
        if self.mode == "json":
            raise RuntimeError("ask() is not available in JSON mode")

        return Menu(
            label=label,
            options=options,
            console=self.console,
            style=self.style,
            inline=inline,
            allow_filtering=allow_filtering,
            multiple=multiple,
            **metadata,
        ).ask()

    @_unavailable_in_json_mode("input")
    def input(
        self,
        title: str,
        default: str = "",
        placeholder: str = "",
        password: bool = False,
        required: bool = False,
        required_message: str = "",
        inline: bool = False,
        value: str = "",
        **metadata: Any,
    ) -> str:
        return Input(
            name=title,
            label=title,
            default=default,
            placeholder=placeholder,
            password=password,
            required=required,
            required_message=required_message,
            inline=inline,
            style=self.style,
            value=value,
            **metadata,
        ).ask()

    def progress(
        self,
        title: str,
        transient: bool = False,
        transient_on_error: bool = False,
        inline_logs: bool = False,
        lines_to_show: int = -1,
        preserve_logs: Optional[bool] = None,
        **metadata: Any,
    ) -> Progress:
        """Create a progress display.

        Args:
            title: Initial progress message.
            transient: Remove the progress display when it finishes.
            transient_on_error: Remove the progress display when it errors.
            inline_logs: Display logged messages as separate lines.
            lines_to_show: Maximum number of inline log lines to display. Negative
                values display all lines.
            preserve_logs: Override the toolkit's progress-log preservation setting.
            **metadata: Additional metadata passed to the style renderer.
        """
        return Progress(
            title=title,
            console=self.console,
            style=self.style,
            transient=True if self.mode == "json" else transient,
            transient_on_error=transient_on_error,
            inline_logs=inline_logs,
            lines_to_show=lines_to_show,
            preserve_logs=(
                self.preserve_progress_logs if preserve_logs is None else preserve_logs
            ),
            quiet=self.mode == "json",
            **metadata,
        )
