---
release type: patch
---

Fix Unicode output on streams using encodings such as ASCII, CP1252, and GBK.
Unsupported characters are displayed as `?`, while supported
characters remain unchanged. For example, `café 🚀` is displayed as
`café ?` on a CP1252 stream.

Built-in decorations use ASCII alternatives when needed. Fix cursor positioning,
empty Fancy-style input rows, and table sizing when encoding fallbacks are used.
Unsupported characters in hyperlink targets are percent-encoded to keep links
working.

Input and menu values remain unchanged. JSON output always uses ASCII with JSON
escapes, including on UTF-8 streams, and restores the original values when decoded.
Add full-suite test coverage for UTF-8, ASCII, CP1252, and GBK in GitHub Actions.
