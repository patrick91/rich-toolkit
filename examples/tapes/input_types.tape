# VHS tape file for input_types example
# Shows different input types

Output website/content/examples/input_types.mp4

Set Theme "Catppuccin Mocha"
Set Width 2000
Set Height 700
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

Type "uv run python examples/demos/input_types.py"
Enter
Sleep 1s

# Email input
Type "user@example.com"
Sleep 300ms
Enter
Sleep 500ms

# Password input
Type "password123"
Sleep 300ms
Enter
Sleep 500ms

# Port input
Type "8080"
Sleep 300ms
Enter
Sleep 1s
