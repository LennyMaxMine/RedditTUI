from textual.widget import Widget
from textual.widgets import Static
from rich.text import Text
from utils.logger import Logger

class Sidebar(Widget):
    def __init__(self, id=None):
        Logger().info("Initializing Sidebar widget")
        super().__init__(id=id)
        self.status = "Home Feed"
        self.account = "Unknown"
        self._sidebar_content = None

    def compose(self):
        Logger().info("Composing Sidebar UI")
        yield Static(id="sidebar_content")

    def on_mount(self):
        Logger().info("Sidebar mounted")
        self._sidebar_content = self.query_one("#sidebar_content", Static)
        self.refresh()

    def update_status(self, status: str):
        Logger().info(f"Updating sidebar status to: {status}")
        self.status = status
        self.refresh()

    def update_sidebar_account(self, account: str):
        Logger().info(f"Updating sidebar account to: {account}")
        self.account = account
        self.refresh()

    def render(self):
        Logger().debug("Sidebar render called, updating static content")
        if self._sidebar_content:
            content = Text()
            content.append(f"Logged in as:\n\n", style="bold blue")
            content.append(f"{self.account}\n\n", style="white")
            content.append("Current View:\n\n", style="bold blue")
            content.append(f"{self.status}\n\n", style="white")
            content.append("Key Bindings:\n\n", style="bold blue")
            content.append("h - Home Feed\n", style="white")
            content.append("n - New Feed\n", style="white")
            content.append("t - Top Feed\n", style="white")
            content.append("s - Search\n", style="white")
            content.append("l - Login\n", style="white")
            content.append("? - Help\n", style="white")
            content.append("c - Settings\n", style="white")
            content.append("e - Edit Theme\n", style="white")
            content.append("q - Quit\n", style="white")
            self._sidebar_content.update(content)

        return Text("")