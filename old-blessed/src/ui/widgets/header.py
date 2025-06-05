from blessed import Terminal

class Header:
    def __init__(self, terminal):
        self.terminal = terminal
        self.title = "Reddit TUI"

    def display(self):
        width = self.terminal.width
        output = []
        output.append(f"╭{'─' * (width-2)}╮")
        output.append(f"│{self.title.center(width-2)}│")
        output.append(f"╰{'─' * (width-2)}╯")
        return "\n".join(output)

    def update_title(self, new_title):
        self.title = new_title