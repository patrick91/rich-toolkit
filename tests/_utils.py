def trim_whitespace_on_lines(text: str) -> str:
    return "\n".join(line.strip() for line in text.splitlines())
