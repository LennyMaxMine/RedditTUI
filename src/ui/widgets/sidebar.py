from blessed import Terminal

class Sidebar:
    def __init__(self, terminal):
        self.terminal = terminal
        self.options = [
            "Home",
            #"View Post",
            "Search",
            "Login",
            "Help",
            "Exit"
        ]
        self.selected_index = 0

    def display(self):
        width = 20
        output = []
        output.append("=" * width)
        output.append("Navigation".center(width))
        output.append("=" * width)
        
        for idx, option in enumerate(self.options):
            if idx == self.selected_index:
                prefix = "> "
            else:
                prefix = "  "
            output.append(f"{prefix}{option}")
        
        return "\n".join(output)

    def navigate(self, direction):
        if direction == "down":
            self.selected_index = (self.selected_index + 1) % len(self.options)
        elif direction == "up":
            self.selected_index = (self.selected_index - 1) % len(self.options)

    def get_selected_option(self):
        return self.options[self.selected_index]