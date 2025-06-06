from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Static
from textual.binding import Binding
from textual.screen import Screen
from services.reddit_service import RedditService
from components.post_list import PostList
from components.login_screen import LoginScreen
from utils.logger import Logger

class RedditTUI(App):
    CSS = """
    Screen {
        background: $surface;
    }

    #sidebar {
        width: 20;
        background: $panel;
        border-right: solid $primary;
    }

    #content {
        width: 1fr;
        background: $surface;
    }

    .sidebar-item {
        padding: 1;
        background: $boost;
    }

    .sidebar-item:hover {
        background: $accent;
    }

    .sidebar-item.selected {
        background: $accent;
        color: $text;
    }

    #login_container {
        width: 100%;
        height: 100%;
        align: center middle;
    }

    #login_form {
        width: 50;
        height: auto;
        background: $surface;
        border: solid $primary;
        padding: 2;
    }

    .title {
        text-align: center;
        color: $text;
        padding: 1;
        text-style: bold;
    }

    Input {
        margin: 1 0;
    }

    Button {
        margin: 1 0;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("h", "home", "Home", show=True),
        Binding("n", "new", "New", show=True),
        Binding("t", "top", "Top", show=True),
        Binding("s", "search", "Search", show=True),
        Binding("l", "login", "Login", show=True),
        Binding("?", "help", "Help", show=True),
        Binding("c", "settings", "Settings", show=True),
        Binding("up", "cursor_up", "Up", show=True),
        Binding("down", "cursor_down", "Down", show=True),
        Binding("enter", "select", "Select", show=True),
    ]

    def __init__(self):
        Logger().info("RedditTUI app initializing")
        super().__init__()
        self.reddit_service = RedditService()
        self.current_feed = "hot"

    def compose(self) -> ComposeResult:
        Logger().info("Composing main UI")
        yield Header()
        with Horizontal():
            yield Static("Home\nNew\nTop\nSearch\nLogin\nHelp\nSettings", id="sidebar")
            yield PostList(id="content")
        yield Footer()

    def on_mount(self) -> None:
        Logger().info("App mounted. Attempting auto-login.")
        if self.reddit_service.auto_login():
            self.action_home()
        else:
            self.action_login()

    def action_quit(self) -> None:
        Logger().info("App quitting.")
        self.exit()

    def action_home(self) -> None:
        Logger().info("Action: home feed")
        self.current_feed = "hot"
        posts = self.reddit_service.get_hot_posts()
        self.query_one(PostList).update_posts(posts)

    def action_new(self) -> None:
        Logger().info("Action: new feed")
        self.current_feed = "new"
        posts = self.reddit_service.get_new_posts()
        self.query_one(PostList).update_posts(posts)

    def action_top(self) -> None:
        Logger().info("Action: top feed")
        self.current_feed = "top"
        posts = self.reddit_service.get_top_posts()
        self.query_one(PostList).update_posts(posts)

    def action_search(self) -> None:
        Logger().info("Action: search")
        pass

    async def action_login(self) -> None:
        Logger().info("Action: login")
        try:
            login_screen = LoginScreen()
            Logger().info("Pushing login screen")
            result = await self.push_screen(login_screen)
            Logger().info(f"Login screen result: {result}")
            if result:
                Logger().info("Login successful, transitioning to home screen")
                self.action_home()
        except Exception as e:
            Logger().error(f"Exception in action_login: {str(e)}", exc_info=True)
            self.notify(f"Error: {str(e)}", severity="error")

    def action_help(self) -> None:
        Logger().info("Action: help")
        pass

    def action_settings(self) -> None:
        Logger().info("Action: settings")
        pass

    def action_select(self) -> None:
        Logger().info("Action: select post")
        post = self.query_one(PostList).get_selected_post()
        if post:
            Logger().info(f"Selected post: {getattr(post, 'title', str(post))}")
            pass

if __name__ == "__main__":
    Logger().info("Starting RedditTUI app")
    app = RedditTUI()
    app.run()
    Logger().info("RedditTUI app exited")
