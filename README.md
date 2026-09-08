# Rich Toolkit

This is a very opinionated set of components for building CLI applications.
It is based on [Rich](https://github.com/Textualize/rich)

## Installation

```bash
pip install rich-toolkit
```

## Example usage

Rich toolkit comes with an `App` class, this is used to give a consistent
style to your CLI application, it can be used as a context manager, like so:

```python
TODO: new example
```

## Output encoding

The consoles created by Rich Toolkit respect the output stream's encoding.
Characters that the stream can encode are printed unchanged. Unsupported
characters in human-readable content are replaced with `?`:
for example, `café 🚀` becomes `café ?` on a CP1252 stream.
Stored input and menu values are never changed by this display conversion.

Built-in menu markers and style decorations use ASCII alternatives when needed.
Custom styles can use `self.symbol("●", fallback=">")` for decorations and
`self.display_text(value)` when measuring or positioning arbitrary text.
Rich `Text` is converted before wrapping, with table cells and common layout
wrappers also prepared before measurement. Styles and links are preserved.
Unsupported characters in hyperlink targets
are percent-encoded as UTF-8, preserving the destination. Custom
renderables emitting raw `Segment` objects also get a final encoding fallback;
they should prepare text before computing their own layout to account for the
changed character widths.

JSON output always uses ASCII with JSON escapes for Unicode characters, including
on UTF-8 streams. Decoding the JSON restores the original values.

The library does not reconfigure `sys.stdout` or `sys.stderr`. Human-readable
encoding fallbacks apply to the toolkit's default consoles; a custom replacement
console is responsible for its own encoding policy.

## Running tests with an encoding

Run the entire suite with a selected output encoding:

```bash
PYTHONIOENCODING=cp1252:strict uv run pytest
```

The suite supports `utf-8` (the default), `ascii`, `cp1252`, and `gbk`. Its
capture streams and in-memory output streams use the selected encoding with
strict errors, including when tests call `capsys.readouterr()`. Individual
encoding regression tests still use their explicitly selected streams.

GitHub Actions runs the full suite in UTF-8 across the Python/Pydantic matrix,
plus ASCII, CP1252, and GBK runs on Python 3.14 with Pydantic v2.
