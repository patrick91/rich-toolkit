import pytest
from _pytest.capture import SysCapture

from ._utils import EncodedOutput, get_output_encoding


class EncodedSysCapture(SysCapture):
    def __init__(self, fd: int) -> None:
        super().__init__(fd, tmpfile=EncodedOutput())


def pytest_report_header() -> str:
    return f"Test output encoding: {get_output_encoding()} (strict)"


@pytest.fixture
def output_encoding() -> str:
    return get_output_encoding()


@pytest.fixture(autouse=True)
def encoded_capture(capsys: pytest.CaptureFixture[str]) -> None:
    """Apply the selected encoding to stdout/stderr for every test."""
    # Pytest recreates these streams between setup, call and teardown. Change
    # the capture factory so each phase uses the selected encoding, including
    # readouterr(), whose default implementation assumes UTF-8.
    capsys.close()
    capsys.captureclass = EncodedSysCapture
    capsys._start()
