from textual.widget import Widget
from textual.widgets import Static
from rich.text import Text
from utils.logger import Logger

class Sidebar(Widget):
    def __init__(self, id=None):
        Logger().info("Initializing Sidebar widget")
        super().__init__(id=id)
        self.status = "Not Logged In"
        self.account = "Not Logged In"
        self.is_logged_in = False
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
        self.is_logged_in = True
        self.refresh()

    def update_auth_status(self, is_logged_in: bool, account: str = "Not Logged In"):
        Logger().info(f"Updating auth status: logged_in={is_logged_in}, account={account}")
        self.is_logged_in = is_logged_in
        self.account = account
        if not is_logged_in:
            self.status = "Not Logged In"
        self.refresh()

    def render(self):
        Logger().debug("Sidebar render called, updating static content")
        if self._sidebar_content:
            content = Text()
            
            if self.is_logged_in:
                content.append(f"Logged in as:\n\n", style="bold blue")
                content.append(f"{self.account}\n\n", style="white")
                content.append("Current View:\n\n", style="bold blue")
                content.append(f"{self.status}\n\n", style="white")
            else:
                content.append(f"Authentication Status:\n\n", style="bold red")
                content.append(f"Not Logged In\n\n", style="red")
                content.append("Please login to use RedditTUI\n\n", style="yellow")
                content.append("Press 'l' to login\n\n", style="yellow")
            
            content.append("Key Bindings:\n\n", style="bold blue")
            content.append("h - Home Feed\n", style="white")
            content.append("n - New Feed\n", style="white")
            content.append("t - Top Feed\n", style="white")
            content.append("s - Advanced Search\n", style="white")
            content.append("b - Saved Posts\n", style="white")
            content.append("r - Subscribed Subreddits\n", style="white")
            content.append("p - Create Post\n", style="white")
            content.append("l - Login\n", style="white")
            content.append("i - Credits\n", style="white")
            content.append("z - Rate Limit Info\n", style="white")
            content.append("x - Create Theme\n", style="white")
            content.append("m - Messages\n", style="white")
            content.append("a - Account Management\n", style="white")
            content.append("v - Subreddit Management\n", style="white")
            content.append("f - Search Subreddits\n", style="white")
            content.append("g - Search Users\n", style="white")
            content.append("? - Help\n", style="white")
            content.append("c - Settings\n", style="white")
            content.append("u - My Profile\n", style="white")
            content.append("q - Quit\n", style="white")
            self._sidebar_content.update(content)

        return Text("")