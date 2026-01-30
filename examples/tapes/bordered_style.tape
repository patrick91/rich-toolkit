# VHS tape file for bordered_style example
# Shows the bordered style

Output website/content/examples/bordered_style.mp4

Set Theme "Catppuccin Mocha"
Set Width 2000
Set Height 800
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

Type "uv run python examples/demos/bordered_style.py"
Enter
Sleep 1s

# Type name
Type "John"
Sleep 300ms
Enter
Sleep 500ms

# Accept default directory
Enter
Sleep 1s
