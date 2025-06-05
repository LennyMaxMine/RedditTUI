from blessed import Terminal

class Sidebar:
    def __init__(self, terminal):
        self.terminal = terminal
        self.options = [
            "Home",
            "New",
            "Top",
            "Saved",
            "Messages",
            "Search",
            "Subreddits",
            "Profile",
            "Help",
            "Settings",
            "Exit"
        ]
        self.selected_index = 0
        self.active = False
        self.width = 20
        self._init_static_parts()

    def _init_static_parts(self):
        self.header = [
            f"├{'─' * (self.width-1)}┬",
            f"│{'Navigation'.center(self.width-1)}│",
            f"├{'─' * (self.width-1)}┤"
        ]
        self.footer = f"╰{'─' * (self.width-1)}╯"
        self.option_lines = [f"│   {option.ljust(self.width-4)}│" for option in self.options]

    def escape_to_home(self):
        self.selected_index = 0
        self._update_selection()

    def display(self):
        output = []
        output.extend(self.header)
        output.extend(self.option_lines)
        output.append(self.footer)
        return "\n".join(output)

    def _update_selection(self):
        if not self.active:
            return
        for i, line in enumerate(self.option_lines):
            if i == self.selected_index:
                self.option_lines[i] = f"│ ► {self.options[i].ljust(self.width-4)}│"
            else:
                self.option_lines[i] = f"│   {self.options[i].ljust(self.width-4)}│"

    def navigate(self, direction):
        old_index = self.selected_index
        if direction == "down":
            self.selected_index = (self.selected_index + 1) % len(self.options)
        elif direction == "up":
            self.selected_index = (self.selected_index - 1) % len(self.options)
        
        if old_index != self.selected_index:
            self._update_selection()

    def get_selected_option(self):
        return self.options[self.selected_index]