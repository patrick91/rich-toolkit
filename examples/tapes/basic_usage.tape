# VHS tape file for basic_usage example
# Generates an MP4 showing basic Rich Toolkit usage

Output website/content/examples/basic_usage.mp4

# Settings
Set Theme "Catppuccin Mocha"
Set Width 2000
Set Height 800
Set FontSize 32
Set Padding 40

# Force color output with true color support
Env FORCE_COLOR "1"
Env TERM "xterm-256color"
Env COLORTERM "truecolor"

# Run the example (we'll create a wrapper script)
Type "uv run python examples/demos/basic_usage.py"
Enter
Sleep 1s

# Type name
Type "John"
Sleep 300ms
Enter
Sleep 500ms

# Accept default directory (just press Enter)
Enter
Sleep 500ms

# Confirm
Type "y"
Sleep 300ms
Enter
Sleep 1s
