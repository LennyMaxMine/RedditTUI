from blessed import Terminal

class Header:
    def __init__(self, terminal):
        self.terminal = terminal
        self.title = "Reddit TUI"

    def display(self):
        width = self.terminal.width
        border = "=" * width
        title_line = self.title.center(width)
        return f"{border}\n{title_line}\n{border}"

    def update_title(self, new_title):
        self.title = new_title