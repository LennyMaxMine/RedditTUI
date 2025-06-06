from textual.widget import Widget
from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text
from utils.logger import Logger

class Sidebar(Widget):
    selected_index = reactive(0)

    def __init__(self, id=None):
        Logger().info("Initializing Sidebar widget")
        super().__init__(id=id)
        self.items = [
            "Home",
            "New",
            "Top",
            "Search",
            "Login",
            "Help",
            "Settings"
        ]
        self.can_focus = True
        self._sidebar_content = None

    def compose(self):
        Logger().info("Composing Sidebar UI")
        yield Static(id="sidebar_content")

    def on_mount(self):
        Logger().info("Sidebar mounted")
        self._sidebar_content = self.query_one("#sidebar_content", Static)
        self.refresh()

    def on_focus(self, event):
        Logger().debug("Sidebar focused")
        self.refresh()

    def on_blur(self, event):
        Logger().debug("Sidebar unfocused")
        self.refresh()

    def render(self):
        Logger().debug("Sidebar render called, updating static content")
        if self._sidebar_content:
            content = []
            for i, item in enumerate(self.items):
                prefix = "▶ " if i == self.selected_index else "  "
                line = Text()
                line.append(prefix, "bold blue" if i == self.selected_index else "white")
                line.append(f"{item}\n", "bold white" if i == self.selected_index else "white")
                content.append(line)
            self._sidebar_content.update(Text.assemble(*content))

        return Text("")

    def action_cursor_up(self):
        Logger().debug("Cursor up in Sidebar")
        if self.selected_index > 0:
            self.selected_index -= 1
            self.refresh()

    def action_cursor_down(self):
        Logger().debug("Cursor down in Sidebar")
        if self.selected_index < len(self.items) - 1:
            self.selected_index += 1
            self.refresh()

    def get_selected_item(self):
        if 0 <= self.selected_index < len(self.items):
            Logger().info(f"Selected item: {self.items[self.selected_index]}")
            return self.items[self.selected_index]
        return None 