import codecs
import io
import os

from _pytest.capture import CaptureIO


def get_output_encoding() -> str:
    encoding = os.environ.get("PYTHONIOENCODING", "utf-8").partition(":")[0] or "utf-8"
    return codecs.lookup(encoding).name


class EncodedOutput(CaptureIO):
    """An in-memory output stream that enforces the suite's selected encoding."""

    def __init__(self) -> None:
        super().__init__()
        self.reconfigure(encoding=get_output_encoding(), errors="strict")

    def getvalue(self) -> str:
        self.flush()
        assert isinstance(self.buffer, io.BytesIO)
        return self.buffer.getvalue().decode(self.encoding)


def trim_whitespace_on_lines(text: str) -> str:
    return "\n".join(line.strip() for line in text.splitlines())
