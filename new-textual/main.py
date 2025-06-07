from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Static
from textual.binding import Binding
from textual.screen import Screen
from services.reddit_service import RedditService
from components.post_list import PostList
from components.sidebar import Sidebar
from components.login_screen import LoginScreen
from components.post_view_screen import PostViewScreen
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
        padding: 1;
    }

    #sidebar_content {
        width: 100%;
        height: 100%;
    }

    #content {
        width: 1fr;
        background: $surface;
        height: 100%;
    }

    #post_container {
        height: 100%;
        overflow-y: scroll;
    }

    #post_content {
        height: auto;
        padding: 1;
    }

    #post_list {
        width: 100%;
        height: auto;
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

    #post_title {
        padding: 1;
        border-bottom: solid $primary;
        margin-bottom: 1;
    }

    #post_metadata {
        color: $text-muted;
        padding: 0 1;
        margin-bottom: 1;
    }

    #post_content {
        padding: 1;
        border: solid $primary;
        margin: 1;
        height: 1fr;
        overflow-y: scroll;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("up", "cursor_up", "Up", show=True),
        Binding("down", "cursor_down", "Down", show=True),
        Binding("enter", "select", "Select", show=True),
        Binding("tab", "switch_focus", "Switch Focus", show=True),
        Binding("l", "login", "Login", show=True),
    ]

    def __init__(self):
        Logger().info("RedditTUI app initializing")
        super().__init__()
        self.reddit_service = RedditService()
        self.current_feed = "hot"
        self.active_widget = "sidebar"
        self.current_posts = []  # Store current posts

    def compose(self) -> ComposeResult:
        Logger().info("Composing main UI")
        yield Header()
        with Horizontal():
            yield Sidebar(id="sidebar")
            yield PostList(id="content")
        yield Footer()

    def on_mount(self) -> None:
        Logger().info("App mounted. Attempting auto-login.")
        self.query_one(Sidebar).focus()
        if self.reddit_service.auto_login():
            self.action_home()
        else:
            self.action_login()

    def action_quit(self) -> None:
        Logger().info("App quitting.")
        self.exit()

    def action_switch_focus(self) -> None:
        Logger().debug("Switching focus")
        if self.active_widget == "sidebar":
            self.active_widget = "content"
            self.query_one(PostList).focus()
        else:
            self.active_widget = "sidebar"
            self.query_one(Sidebar).focus()

    def action_cursor_up(self) -> None:
        Logger().debug("Cursor up action")
        if self.active_widget == "sidebar":
            self.query_one(Sidebar).action_cursor_up()
        else:
            self.query_one(PostList).action_cursor_up()

    def action_cursor_down(self) -> None:
        Logger().debug("Cursor down action")
        if self.active_widget == "sidebar":
            self.query_one(Sidebar).action_cursor_down()
        else:
            self.query_one(PostList).action_cursor_down()

    def action_select(self) -> None:
        Logger().info("Action: select")
        if self.active_widget == "sidebar":
            item = self.query_one(Sidebar).get_selected_item()
            if item:
                self._handle_sidebar_action(item)
        else:
            post = self.query_one(PostList).get_selected_post()
            if post:
                Logger().info(f"Selected post: {getattr(post, 'title', str(post))}")
                content = self.query_one("#content")
                content.remove_children()
                content.mount(PostViewScreen(post, content, self.current_posts))

    def _handle_sidebar_action(self, item: str) -> None:
        Logger().info(f"Handling sidebar action: {item}")
        if item == "Home":
            self.action_home()
        elif item == "New":
            self.action_new()
        elif item == "Top":
            self.action_top()
        elif item == "Search":
            self.action_search()
        elif item == "Login":
            self.action_login()
        elif item == "Help":
            self.action_help()
        elif item == "Settings":
            self.action_settings()

    def action_home(self) -> None:
        Logger().info("Action: home feed")
        self.current_feed = "hot"
        posts = self.reddit_service.get_hot_posts()
        self.current_posts = posts  # Store posts
        self.query_one(PostList).update_posts(posts)
        self.active_widget = "content"
        self.query_one(PostList).focus()

    def action_new(self) -> None:
        Logger().info("Action: new feed")
        self.current_feed = "new"
        posts = self.reddit_service.get_new_posts()
        self.current_posts = posts  # Store posts
        self.query_one(PostList).update_posts(posts)
        self.active_widget = "content"
        self.query_one(PostList).focus()

    def action_top(self) -> None:
        Logger().info("Action: top feed")
        self.current_feed = "top"
        posts = self.reddit_service.get_top_posts()
        self.current_posts = posts  # Store posts
        self.query_one(PostList).update_posts(posts)
        self.active_widget = "content"
        self.query_one(PostList).focus()

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
                Logger().info("Login successful, reinitializing RedditService")
                self.reddit_service = RedditService()
                if self.reddit_service.auto_login():
                    Logger().info("Auto-login successful after manual login")
                    self.action_home()
                else:
                    Logger().error("Failed to reinitialize RedditService after login")
                    self.notify("Error: Failed to initialize Reddit service", severity="error")
                    self.action_home()
            else:
                Logger().info("Login cancelled or failed, returning to home")
                self.action_home()
        except Exception as e:
            Logger().error(f"Exception in action_login: {str(e)}", exc_info=True)
            self.notify(f"Error: {str(e)}", severity="error")
            self.action_home()

    def action_help(self) -> None:
        Logger().info("Action: help")
        pass

    def action_settings(self) -> None:
        Logger().info("Action: settings")
        pass

if __name__ == "__main__":
    Logger().info("Starting RedditTUI app")
    app = RedditTUI()
    app.run()
    Logger().info("RedditTUI app exited")
