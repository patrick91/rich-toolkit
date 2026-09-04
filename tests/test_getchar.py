import builtins
import sys
from io import StringIO

import pytest

from rich_toolkit._getchar import getchar
from rich_toolkit.container import Container
from rich_toolkit.input import Input
from rich_toolkit.styles import MinimalStyle


@pytest.mark.skipif(sys.platform == "win32", reason="Unix terminal behavior")
def test_getchar_raises_eoferror_when_no_terminal_is_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sys, "stdin", StringIO())

    def unavailable_terminal(*args: object, **kwargs: object) -> None:
        raise OSError(6, "No such device or address", "/dev/tty")

    monkeypatch.setattr(builtins, "open", unavailable_terminal)

    with pytest.raises(
        EOFError, match="No terminal is available for interactive input"
    ):
        getchar()


def test_container_restores_cancelled_input_before_propagating_eof(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    style = MinimalStyle(theme={})
    input_field = Input(label="Name", style=style)
    container = Container(style=style)
    container.elements = [input_field]
    refresh_states: list[bool] = []

    monkeypatch.setattr(
        "rich_toolkit.container.getchar",
        lambda: (_ for _ in ()).throw(EOFError()),
    )
    monkeypatch.setattr(
        container,
        "_refresh",
        lambda done=False: refresh_states.append(done),
    )

    with pytest.raises(EOFError):
        container.run()

    assert input_field._cancelled is True
    assert refresh_states == [False, True]
