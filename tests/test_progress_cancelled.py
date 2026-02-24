from __future__ import annotations

from rich.text import Text

from rich_toolkit.progress import Progress
from rich_toolkit.styles.base import BaseStyle
from rich_toolkit.styles.border import BorderedStyle


def test_progress_cancelled_flag_set_on_keyboard_interrupt():
    """KeyboardInterrupt during progress should set _cancelled to True."""
    style = BaseStyle()
    progress = Progress("Installing...", style=style)

    progress.start()
    progress.__exit__(KeyboardInterrupt, None, None)

    assert progress._cancelled is True


def test_progress_cancelled_flag_not_set_on_normal_exit():
    """Normal exit should not set _cancelled."""
    style = BaseStyle()
    progress = Progress("Installing...", style=style)

    progress.start()
    progress.__exit__(None, None, None)

    assert progress._cancelled is False


def test_render_cancelled_progress_base_style():
    """Cancelled progress should render title with 'Cancelled.' in base style."""
    style = BaseStyle()
    progress = Progress("Installing...", style=style)
    progress._cancelled = True

    result = style.render_progress(progress, done=True)

    assert isinstance(result, Text)
    assert "Installing..." in result.plain
    assert "Cancelled." in result.plain


def test_render_cancelled_progress_border_style():
    """Cancelled progress should render 'Cancelled.' in border style."""
    style = BorderedStyle()
    progress = Progress("Installing...", style=style)
    progress._cancelled = True

    result = style.render_progress(progress, done=True)

    # Border style wraps in a box, so check the rendered string
    style.console.begin_capture()
    style.console.print(result)
    output = style.console.end_capture()

    assert "Cancelled." in output


def test_render_non_cancelled_progress_does_not_show_cancelled():
    """Normal (non-cancelled) progress should not show 'Cancelled.'."""
    style = BaseStyle()
    progress = Progress("Installing...", style=style)

    result = style.render_progress(progress, done=True)

    # result is the current_message string, not a Text with "Cancelled."
    if isinstance(result, Text):
        assert "Cancelled." not in result.plain
    else:
        assert "Cancelled." not in str(result)
