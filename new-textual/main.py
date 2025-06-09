from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Static, Button
from textual.binding import Binding
from textual.screen import Screen
from textual.theme import Theme
from services.reddit_service import RedditService
from components.post_list import PostList
from components.sidebar import Sidebar
from components.login_screen import LoginScreen
from components.post_view_screen import PostViewScreen
from components.search_screen import SearchScreen
from components.settings_screen import SettingsScreen
from utils.logger import Logger
import json
import os
from pathlib import Path

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

    #settings_container {
        width: 100%;
        height: 100%;
        align: center middle;
    }

    #settings_form {
        width: 50;
        height: auto;
        background: $surface;
        border: solid $primary;
        padding: 2;
    }

    #theme_container {
        width: 1fr;
        height: 100%;
        align: center middle;
    }

    #theme_form {
        width: 50;
        max-width: 80vw;
        min-width: 30;
        margin: 2 2;
        background: $surface;
        border: solid $primary;
        padding: 2;
    }

    .color_label {
        width: 14;
        min-width: 10;
        text-align: right;
        padding-right: 1;
    }

    .color_preview {
        width: 5;
        height: 2;
        border: solid $primary;
        background: $background;
        margin-left: 1;
    }

    #theme_form Horizontal {
        width: 100%;
        align: left middle;
        margin-bottom: 1;
    }

    #theme_form Input {
        width: 18;
        height: 2;
        margin: 0 1;
    }

    #theme_form Button {
        min-width: 10;
    }

    #button_container {
        align: center middle;
        height: auto;
        margin-top: 2;
    }

    .title {
        text-align: center;
        color: $text;
        padding: 1;
        text-style: bold;
    }

    .setting_label {
        color: $text;
        padding: 1 0;
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

    #comments_container {
        height: 1fr;
        min-height: 0;
        overflow-y: scroll;
        border: solid $primary;
        margin: 1;
    }

    #comments_section {
        padding: 1;
        width: 100%;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("enter", "select", "Select", show=True),
        Binding("h", "home", "Home", show=True),
        Binding("n", "new", "New", show=True),
        Binding("t", "top", "Top", show=True),
        Binding("s", "search", "Search", show=True),
        Binding("l", "login", "Login", show=True),
        Binding("?", "help", "Help", show=True),
        Binding("c", "settings", "Settings", show=True),
    ]

    def __init__(self):
        Logger().info("RedditTUI app initializing")
        super().__init__()
        self.reddit_service = RedditService()
        self.current_feed = "hot"
        self.current_posts = []
        self.settings = self.load_settings()
        Logger().info("Registered bindings: " + str(self.BINDINGS))

    def on_mount(self) -> None:
        Logger().info("================================ App mounted ==================================")

        for file in os.listdir("themes"):
            if file.endswith(".theme"):
                Logger().info(f"Loading theme: {file}")
                with open(os.path.join("themes", file), "r") as f:
                    theme = json.load(f)
                    self.register_theme(Theme(**theme))
                    Logger().info(f"Registered theme: {theme['name']}")

        self.theme = self.settings.get("theme", "dark")

        Logger().info(f"Attempting auto-login")
        if self.reddit_service.auto_login():
            self.action_home()
            self.query_one(Sidebar).update_sidebar_account(self.reddit_service.user)
            Logger().info(f"Auto-login successful")
        else:
            Logger().info(f"Auto-login failed, attempting manual login")
            self.action_login()

        Logger().info("================================ On_mount finished ==================================")

    def compose(self) -> ComposeResult:
        Logger().info("Composing main UI")
        yield Header()
        with Horizontal():
            yield Sidebar(id="sidebar")
            yield PostList(id="content")
        yield Footer()

    def action_quit(self) -> None:
        Logger().debug("App quitting.")
        self.exit()

    def on_key(self, event):
        Logger().info(f"Key pressed: {event.key}")
        return event

    def action_select(self) -> None:
        Logger().info("Action: select")
        post = self.query_one(PostList).get_selected_post()
        if post:
            Logger().info(f"Selected post: {getattr(post, 'title', str(post))}")
            content = self.query_one("#content")
            content.remove_children()
            content.mount(PostViewScreen(post, content, self.current_posts))

    def action_home(self) -> None:
        Logger().info("Action: home feed")
        self.current_feed = "hot"
        posts = self.reddit_service.get_hot_posts()
        self.current_posts = posts
        self.query_one(PostList).update_posts(posts)
        self.query_one(Sidebar).update_status("Home Feed")
        self.query_one(PostList).focus()

    def action_new(self) -> None:
        Logger().info("Action: new feed")
        self.current_feed = "new"
        posts = self.reddit_service.get_new_posts()
        self.current_posts = posts
        self.query_one(PostList).update_posts(posts)
        self.query_one(Sidebar).update_status("New Feed")
        self.query_one(PostList).focus()

    def action_top(self) -> None:
        Logger().info("Action: top feed")
        self.current_feed = "top"
        posts = self.reddit_service.get_top_posts()
        self.current_posts = posts
        self.query_one(PostList).update_posts(posts)
        self.query_one(Sidebar).update_status("Top Feed")
        self.query_one(PostList).focus()

    async def action_search(self) -> None:
        Logger().info("Action: search")
        try:
            content = self.query_one("#content")
            content.remove_children()
            search_screen = SearchScreen(content, self.current_posts)
            content.mount(search_screen)
            self.app.active_widget = "content"
            search_screen.focus()
            self.query_one(Sidebar).update_status("Search Feed")
        except Exception as e:
            Logger().error(f"Error in search action: {str(e)}", exc_info=True)
            self.notify(f"Error: {str(e)}", severity="error")

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

    async def action_settings(self) -> None:
        Logger().info("Action: settings")
        try:
            settings_screen = SettingsScreen()
            result = await self.push_screen(settings_screen)
            if result:
                Logger().info("Settings saved")
                self.apply_settings()
            else:
                Logger().info("Settings cancelled")
        except Exception as e:
            Logger().error(f"Error in settings action: {str(e)}", exc_info=True)
            self.notify(f"Error: {str(e)}", severity="error")

    def load_settings(self) -> dict:
        Logger().info("Loading settings")
        config_dir = Path.home() / ".config" / "reddit-tui"
        settings_file = config_dir / "settings.json"
        
        default_settings = {
            "posts_per_page": 25,
            "comment_depth": 3,
            "auto_load_comments": True,
            "show_nsfw": False,
            "theme": "dark",
            "sort_comments_by": "best"
        }

        try:
            if settings_file.exists():
                with open(settings_file, "r") as f:
                    settings = json.load(f)
                    Logger().info("Settings loaded successfully")
                    return {**default_settings, **settings}
        except Exception as e:
            Logger().error(f"Error loading settings: {str(e)}", exc_info=True)
        
        return default_settings

    def save_settings(self) -> None:
        Logger().info("Saving settings")
        config_dir = Path.home() / ".config" / "reddit-tui"
        settings_file = config_dir / "settings.json"
        
        try:
            config_dir.mkdir(parents=True, exist_ok=True)
            with open(settings_file, "w") as f:
                json.dump(self.settings, f, indent=4)
            Logger().info("Settings saved successfully")
        except Exception as e:
            Logger().error(f"Error saving settings: {str(e)}", exc_info=True)
            self.notify("Error saving settings", severity="error")

    def apply_settings(self) -> None:
        Logger().info("Applying settings")
        try:
            # Apply theme
            self.theme = self.settings.get("theme", "dark")

            # Apply posts per page settings
            if self.current_posts:
                posts = getattr(self.reddit_service, f"get_{self.current_feed}_posts")(limit=self.settings["posts_per_page"])
                self.current_posts = posts
                self.query_one(PostList).update_posts(posts)

            # Apply comment depth setting
            if hasattr(self, "current_post") and self.current_post:
                comments = self.reddit_service.get_post_comments(self.current_post, limit=self.settings["comment_depth"])
                self.query_one(PostViewScreen).update_comments(comments)

            # Apply NSFW filter
            if not self.settings["show_nsfw"]:
                self.current_posts = [post for post in self.current_posts if not getattr(post, "over_18", False)]
                self.query_one(PostList).update_posts(self.current_posts)

            # Apply comment sort setting
            if hasattr(self, "current_post") and self.current_post:
                self.query_one(PostViewScreen).sort_comments(self.settings["sort_comments_by"])

            # Apply auto load comments setting
            if hasattr(self, "current_post") and self.current_post:
                if self.settings["auto_load_comments"]:
                    self.query_one(PostViewScreen).load_comments()
                else:
                    self.query_one(PostViewScreen).clear_comments()

            self.refresh()
            Logger().info("Settings applied successfully")
        except Exception as e:
            Logger().error(f"Error applying settings: {str(e)}", exc_info=True)
            self.notify("Error applying settings", severity="error")

if __name__ == "__main__":
    Logger().info("Starting RedditTUI app")
    app = RedditTUI()
    app.run()
    Logger().info("RedditTUI app exited")
