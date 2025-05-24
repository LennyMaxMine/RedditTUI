from blessed import Terminal

class Sidebar:
    def __init__(self, terminal):
        self.terminal = terminal
        self.options = [
            "Home",
            "Popular",
            "All",
            "Explore",
            "Search",
            "Subreddits",
            #"Profile",
            "Help",
            "Settings",
            "Exit"
        ]
        self.selected_index = 0

    def display(self):
        width = 20
        output = []
        output.append(f"├{'─' * (width-1)}┬")
        output.append(f"│{'Navigation'.center(width-1)}│")
        output.append(f"├{'─' * (width-1)}┤")
        
        for idx, option in enumerate(self.options):
            if idx == self.selected_index:
                prefix = "│ ► "
            else:
                prefix = "│   "
            output.append(f"{prefix}{option.ljust(width-4)}│")
        
        output.append(f"╰{'─' * (width-1)}╯")
        return "\n".join(output)

    def navigate(self, direction):
        if direction == "down":
            self.selected_index = (self.selected_index + 1) % len(self.options)
        elif direction == "up":
            self.selected_index = (self.selected_index - 1) % len(self.options)

    def get_selected_option(self):
        return self.options[self.selected_index]