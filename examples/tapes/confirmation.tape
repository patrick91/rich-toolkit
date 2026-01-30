# VHS tape file for confirmation example
# Shows confirmation prompts

Output website/content/examples/confirmation.mp4

Set Theme "Catppuccin Mocha"
Set Width 2000
Set Height 600
Set FontSize 32
Set Padding 40

# Force color output with true color support
Env FORCE_COLOR "1"
Env TERM "xterm-256color"
Env COLORTERM "truecolor"

# Set a clean prompt using Hide/Show
Hide
Type "PS1='$ '"
Enter
Ctrl+L
Show

Type "uv run python examples/demos/confirmation.py"
Enter
Sleep 1s

# First confirmation - Yes
Type "y"
Sleep 300ms
Enter
Sleep 500ms

# Second confirmation - No
Type "n"
Sleep 300ms
Enter
Sleep 1s
