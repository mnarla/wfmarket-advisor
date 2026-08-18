Output assets/demo.gif
Output assets/demo.mp4

Set Shell "zsh"
Set FontSize 14
Set Width 1100
Set Height 750
Set Padding 25
Set Theme "Catppuccin Mocha"
Set WindowBar "Colorful"
Set TypingSpeed 50ms

# Setup environment cleanly
Hide
Type "source venv/bin/activate"
Enter
Type "clear"
Enter
Sleep 1s
Show

# Start interactive CLI tool
Type "python main.py"
Sleep 500ms
Enter
Sleep 2.5s

# 1. Query: Caliban Prime Systems
Type "caliban p sys"
Sleep 500ms
Enter
Sleep 8s

# 2. Query: Soma Prime
Type "soma p"
Sleep 500ms
Enter
Sleep 8s

# Exit cleanly
Type "quit"
Sleep 500ms
Enter
Sleep 2s
