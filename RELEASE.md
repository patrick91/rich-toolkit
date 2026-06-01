---
release type: minor
---

This release adds JSON output support for CLI-friendly structured results.

`RichToolkit(mode="json")` now suppresses human-only rendering and writes JSON-compatible output through `output()`. Pydantic-style models are serialized through `model_dump(mode="json")`, dictionaries and lists remain supported, and generators can be passed to `output()` to stream newline-delimited JSON events.

The release also adds examples showing final JSON output, streaming JSON output, list output, and custom human renderers.
