from abc import ABC, abstractmethod
from typing import Any, Generator, Iterable, List, Type, TypeVar

from rich.color import Color
from rich.console import (
    Console,
    ConsoleOptions,
    ConsoleRenderable,
    RenderableType,
    RenderResult,
)
from rich.segment import Segment
from rich.text import Text
from typing_extensions import Literal

from rich_toolkit.utils.colors import darken_text, lighten
from rich_toolkit.utils.map_range import map_range

ConsoleRenderableClass = TypeVar(
    "ConsoleRenderableClass", bound=Type[ConsoleRenderable]
)


class BaseStyle: ...
