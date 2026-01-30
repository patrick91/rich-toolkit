# VHS tape file for menu_example
# Shows menu selection

Output website/content/examples/menu_example.mp4

Set Theme "Catppuccin Mocha"
Set Width 2000
Set Height 900
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

Type "uv run python examples/demos/menu_example.py"
Enter
Sleep 1s

# Navigate down to Vue and select it
Down
Sleep 500ms
Enter
Sleep 1s
