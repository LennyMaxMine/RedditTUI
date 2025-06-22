from textual.app import App, ComposeResult, SystemCommand
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Static, Button
from textual.binding import Binding
from textual.screen import Screen, ModalScreen
from textual.theme import Theme
from services.reddit_service import RedditService
from components.post_list import PostList
from components.sidebar import Sidebar
from components.login_screen import LoginScreen
from components.post_view_screen import PostViewScreen
from components.settings_screen import SettingsScreen
from components.user_profile_screen import UserProfileScreen
from components.comment_screen import CommentScreen
from components.qr_screen import QRScreen
from components.subreddit_screen import SubredditScreen
from components.post_creation_screen import PostCreationScreen
from components.credits_screen import CreditsScreen
from components.rate_limit_screen import RateLimitScreen
from components.theme_creation_screen import ThemeCreationScreen
from components.messages_screen import MessagesScreen
from components.account_management_screen import AccountManagementWidget
from components.advanced_search_screen import AdvancedSearchScreen
from components.subreddit_management_screen import SubredditManagementScreen
from utils.logger import Logger
import json
import os
from pathlib import Path
from datetime import datetime

class ReportReasonScreen(ModalScreen):
    def __init__(self, reasons):
        super().__init__()
        self.reasons = reasons

    def compose(self):
        yield Static("Select a reason for reporting this post:", classes="title")
        with Vertical():
            for idx, reason in enumerate(self.reasons):
                yield Button(reason, id=f"reason_{idx}")
            yield Button("Back", id="back_button")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "back_button":
            self.dismiss("back")
        else:
            self.dismiss(event.button.label)

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

    #comment_container {
        width: 100%;
        height: 100%;
        align: center middle;
    }

    #comment_form {
        width: 50;
        height: auto;
        background: $surface;
        border: solid $primary;
        padding: 2;
    }

    #comment_input {
        height: 10;
        margin: 1 0;
    }

    #post_container {
        width: 100%;
        height: 100%;
        align: center middle;
    }

    #post_form {
        width: 60;
        height: auto;
        background: $surface;
        border: solid $primary;
        padding: 2;
    }

    .post_content {
        height: 15;
        margin: 1 0;
    }

    #post_form Input {
        width: 100%;
        margin: 1 0;
    }

    #post_form Select {
        width: 100%;
        margin: 1 0;
    }

    #post_form TextArea {
        width: 100%;
        margin: 1 0;
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
        height: 100%;
        min-height: 0;
        overflow-y: scroll;
        border: solid $primary;
        margin: 1;
    }

    #comments_section {
        padding: 1;
        width: 100%;
    }

    #comments_section Panel {
        border: solid $primary;
        padding: 1;
    }

    #comments_section .thread-line {
        color: $primary;
    }

    #comments_section .comment-header {
        margin-bottom: 1;
    }

    #comments_section .comment-body {
        margin-left: 2;
    }

    #search_container {
        width: 100%;
        height: 100%;
        align: center middle;
    }

    #search_form {
        width: 60;
        height: auto;
        background: $surface;
        border: solid $primary;
        padding: 2;
    }

    .section_title {
        color: $text;
        padding: 1 0;
        text-style: bold;
        border-bottom: solid $primary;
        margin: 1 0;
    }

    .filter_label {
        color: $text;
        padding: 1 0;
    }

    #main_filters {
        width: 100%;
        align: left middle;
        margin: 1 0;
    }

    #main_filters Select {
        width: 1fr;
        margin: 0 1;
    }

    #additional_options {
        width: 100%;
        align: left middle;
        margin: 1 0;
    }

    #additional_options Switch {
        margin: 0 1;
    }

    .switch_label {
        color: $text;
        padding: 0 1;
        text-align: right;
        width: 15;
    }

    #search_form .wide_input {
        width: 1fr;
        min-width: 20;
        max-width: 100%;
        margin: 0 1 1 0;
        height: 6;
    }
    #search_form .wide_select {
        width: 1fr;
        min-width: 16;
        max-width: 100%;
        margin: 0 1 1 0;
    }
    .distinct_title {
        text-style: bold;
        color: $primary;
        border-bottom: solid $primary;
        margin-bottom: 1;
        margin-top: 2;
    }
    #filter_row1, #filter_row2 {
        width: 100%;
        align: left middle;
        margin: 1 0 1 0;
    }
    .adv_switch {
        margin: 0 2 0 0;
        min-width: 8;
        align: center middle;
    }
    .search_btn {
        min-width: 12;
        margin: 1 2 1 2;
    }

    .sort_label {
        color: $text;
        padding: 1 0;
        text-align: right;
        width: 15;
    }

    #comment_sort {
        width: 20;
        margin: 0 1;
    }

    #credits_container {
        width: 100%;
        height: 100%;
        align: center middle;
    }

    #credits_form {
        width: 60;
        height: auto;
        max-height: 80vh;
        background: $surface;
        border: solid $primary;
        padding: 2;
    }

    #credits_container ScrollableContainer {
        height: 1fr;
        margin: 1 0;
    }

    #credits_content {
        padding: 1;
    }

    #rate_limit_container {
        width: 100%;
        height: 100%;
        align: center middle;
    }

    #rate_limit_content {
        width: 60;
        height: auto;
        background: $surface;
        border: solid $primary;
        padding: 2;
    }

    .rate_section {
        margin: 1 0;
        padding: 1;
        border-bottom: solid $primary;
    }

    .rate_title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    .rate_value {
        color: $text;
        margin-left: 2;
    }

    .rate_warning {
        color: $warning;
    }

    .rate_critical {
        color: $error;
    }

    .rate_good {
        color: $success;
    }

    #refresh_button {
        margin-top: 2;
    }

    #messages_container {
        width: 100%;
        height: 1fr;
        overflow-y: scroll;
        padding: 2 0;
        align: center top;
    }

    #messages_content {
        width: 60;
        max-width: 90vw;
        min-width: 30;
        margin: 0 2;
        padding: 1 2;
        align: center top;
    }

    #messages_content .message {
        border: solid $primary;
        padding: 1;
        margin: 2 0;
        background: $panel;
        width: 100%;
        max-width: 60;
        min-width: 28;
        align: center top;
        transition: background 0.2s;
    }

    #messages_content .message.unread {
        background: $boost;
        border-left: solid $primary;
    }

    #messages_content .message-header {
        color: $text-muted;
        margin-bottom: 1;
    }

    #messages_content .message-body {
        margin: 1 0;
        padding: 1;
        background: $surface;
        border: solid $primary-lighten-2;
    }

    #messages_content .conversation-header {
        color: $primary;
        text-style: bold;
        margin: 2 0 1 0;
        padding: 1;
        background: $panel-darken-2;
        border-bottom: solid $primary;
    }

    #messages_content .compose-form {
        border: solid $primary;
        padding: 2;
        margin: 2 0;
        background: $panel;
        width: 100%;
        max-width: 60;
        min-width: 28;
        align: center top;
    }

    #messages_content .compose-form Input {
        width: 100%;
        min-width: 20;
        max-width: 100%;
        margin: 1 0;
    }

    #messages_content .compose-form TextArea {
        width: 100%;
        min-width: 20;
        max-width: 100%;
        height: 8;
        margin: 1 0;
    }

    #messages_content .compose-form Button {
        margin: 1 0;
        min-width: 10;
        align: center middle;
    }

    #messages_content .button-container {
        width: 100%;
        align: center middle;
        margin-top: 1;
    }

    #messages_content #search_input {
        width: 20;
        margin: 0 1;
    }

    #messages_content #sort_select,
    #messages_content #filter_select {
        width: 12;
        margin: 0 1;
    }

    #messages_content Horizontal {
        width: 100%;
        align: left middle;
        margin-bottom: 1;
    }
    #messages_panel {
        width: 1fr;
        height: 100%;
        background: $surface;
        padding: 1;
    }

    #messages_panel Button {
        margin: 1 0;
        min-width: 15;
    }

    #conversations_panel Button {
        margin: 1 0;
        min-width: 15;
    }

    #messages_container {
        width: 100%;
        height: 1fr;
        overflow-y: scroll;
        padding: 2 0;
        align: center top;
    }

    .message-actions {
        width: 100%;
        align: center middle;
        margin-top: 1;
    }

    .message-actions Button {
        margin: 0 1;
        min-width: 8;
    }

    .message-header-container {
        margin-bottom: 1;
    }

    #conversations_panel {
        width: 30;
        height: 100%;
        background: $panel;
        border-right: solid $primary;
        padding: 1;
    }

    #conversations_list {
        height: 1fr;
        overflow-y: scroll;
        margin-top: 1;
    }

    .conversation {
        padding: 1;
        margin: 1 0;
        border: solid $primary;
        background: $surface;
        transition: background 0.2s;
    }

    .conversation:hover {
        background: $boost;
    }

    .conversation.selected {
        background: $boost;
        border-left: solid $primary;
    }

    .conversation.unread {
        background: $panel-darken-2;
    }

    .conversation-name {
        text-style: bold;
        color: $text;
    }

    .conversation-preview {
        color: $text-muted;
        margin: 1 0;
    }

    .conversation-time {
        color: $text-muted;
        text-style: italic;
    }

    .unread-badge {
        color: $primary;
        text-style: bold;
        margin-top: 1;
    }

    #account_management_container {
        width: 100%;
        height: 100%;
        align: center top;
        padding: 1;
    }

    #account_list_container {
        width: 60;
        height: auto;
        background: $surface;
        border: solid $primary;
        padding: 2;
    }

    #accounts_list_scroll {
        height: 15;
        border: solid $primary-lighten-2;
        margin: 1 0;
    }

    #add_account_container {
        width: 60;
        height: auto;
        background: $surface;
        border: solid $primary;
        padding: 2;
    }

    .account {
        padding: 1;
        margin: 1 0;
        background: $surface;
        transition: background 0.2s;
    }

    .account:hover {
        background: $boost;
    }

    .account.selected {
        background: $boost;
        border-left: solid $primary;
    }

    .account.current {
        background: $panel-darken-2;
        border-left: solid $success;
    }

    .account.selected.current {
        background: $boost;
        border-left: solid $success;
    }

    .account-name {
        text-style: bold;
        color: $text;
    }

    .account.selected .account-name {
        color: $primary;
    }

    .account-date {
        color: $text-muted;
        margin: 1 0;
    }

    #account_actions {
        width: 100%;
        align: center middle;
        margin-top: 2;
    }

    #account_actions Button {
        margin: 0 1;
        min-width: 12;
    }

    #add_account_actions {
        width: 100%;
        align: center middle;
        margin-top: 2;
    }

    #add_account_actions Button {
        margin: 0 1;
        min-width: 10;
    }

    #add_account_container Input {
        width: 100%;
        margin: 1 0;
    }

    .hidden {
        display: none;
    }

    #startup_account_container {
        width: 100%;
        height: 100%;
        align: center middle;
    }

    #account_selection_container {
        width: 60;
        height: auto;
        background: $surface;
        border: solid $primary;
        padding: 2;
    }

    .subtitle {
        text-align: center;
        color: $text-muted;
        padding: 1;
        margin-bottom: 2;
    }

    #startup_accounts_list {
        height: 20;
        margin: 1 0;
    }

    #startup_account_actions {
        width: 100%;
        align: center middle;
        margin-top: 2;
    }

    #startup_account_actions Button {
        margin: 0 1;
        min-width: 12;
    }

    #startup_account_container .account {
        padding: 1;
        margin: 1 0;
        border: solid $primary;
        background: $surface;
        transition: background 0.2s;
    }

    #startup_account_container .account:hover {
        background: $boost;
    }

    #startup_account_container .account.selected {
        background: $boost;
        border-left: solid $primary;
    }

    #subreddit_management_container {
        width: 100%;
        height: 100%;
    }

    #subreddit_container {
        width: 100%;
        height: 100%;
        background: $surface;
        padding: 2;
    }

    #controls {
        width: 100%;
        align: left middle;
        margin-bottom: 1;
    }

    #controls Select {
        width: 20;
        margin: 0 1;
    }

    #controls Input {
        width: 30;
        margin: 0 1;
    }

    #controls Button {
        min-width: 10;
    }

    #subreddits_table {
        height: 1fr;
        margin: 1 0;
    }

    #actions {
        width: 100%;
        align: center middle;
        margin-top: 1;
    }

    .action_btn {
        margin: 0 1;
        min-width: 12;
    }

    #help_screen_container {
        width: 100%;
        height: 100%;
        align: center middle;
    }

    #help_scroll_container {
        width: 80;
        height: auto;
        max-height: 80vh;
        background: $surface;
        border: solid $primary;
        padding: 2;
    }

    #help_container {
        width: 100%;
        height: auto;
    }

    .help_content {
        padding: 1;
        min-height: 1.2;
    }

    #help_actions {
        width: 100%;
        align: center middle;
        margin-top: 1;
    }

    .help_btn {
        min-width: 10;
    }

    #account_management_wrapper {
        align: center middle;
        height: 100%;
    }

    #account_management_widget {
        width: 60;
        max-height: 80vh;
        background: $surface;
        border: solid $primary;
        padding: 1;
    }

    #view_container {
        height: 1fr;
        border: solid $primary-lighten-2;
        margin: 1 0;
    }

    .add_account_form {
        padding: 0 1;
    }

    .add_account_form Input {
        margin-bottom: 1;
    }

    #account_actions {
        width: 100%;
        align: center middle;
        margin-top: 2;
    }

    #add_account_actions {
        align: center middle;
        margin-top: 2;
    }

    #add_account_actions Button {
        margin: 0 1;
        min-width: 10;
    }

    #add_account_container Input {
        width: 100%;
        margin: 1 0;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("enter", "select", "Select", show=True),
        Binding("h", "home", "Home", show=True),
        Binding("n", "new", "New", show=True),
        Binding("t", "top", "Top", show=True),
        Binding("s", "advanced_search", "Advanced Search", show=True),
        Binding("l", "login", "Login", show=True),
        Binding("?", "help", "Help", show=True),
        Binding("c", "settings", "Settings", show=True),
        Binding("u", "my_profile", "My Profile", show=True),
        Binding("b", "saved_posts", "Saved Posts", show=True),
        Binding("r", "subscribed_subreddits", "Subscribed Subreddits", show=True),
        Binding("p", "create_post", "Create Post", show=True),
        Binding("i", "credits", "Credits", show=True),
        Binding("z", "rate_limit", "Rate Limit Info", show=True),
        Binding("x", "create_theme", "Create Theme", show=True),
        Binding("m", "messages", "Messages", show=True),
        Binding("a", "account_management", "Account Management", show=True),
        Binding("v", "subreddit_management", "Subreddit Management", show=True),
        Binding("f", "search_subreddits", "Search Subreddits", show=True),
        Binding("g", "search_users", "Search Users", show=True),
    ]

    def __init__(self):
        Logger().info("RedditTUI app initializing")
        super().__init__()
        self.reddit_service = None
        self.current_feed = "hot"
        self.current_posts = []
        self.settings = self.load_settings()
        self.logger = Logger()
        Logger().info("Registered bindings: " + str(self.BINDINGS))

    async def on_mount(self) -> None:
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
        if self.reddit_service is None:
            self.reddit_service = RedditService()
        
        if len(self.reddit_service.accounts) > 0:
            Logger().info(f"Found {len(self.reddit_service.accounts)} accounts, attempting auto-login")
            if self.reddit_service.auto_login():
                self.action_home()
                current_account = self.reddit_service.get_current_account()
                if current_account:
                    self.query_one(Sidebar).update_sidebar_account(current_account)
                Logger().info(f"Auto-login successful")
            else:
                Logger().info(f"Auto-login failed, showing login screen")
                self.query_one(Sidebar).update_auth_status(False)
                await self.show_login_if_not_authenticated()
        else:
            Logger().info("No accounts found, showing login screen")
            self.query_one(Sidebar).update_auth_status(False)
            await self.show_login_if_not_authenticated()

        Logger().info("================================ On_mount finished ==================================")

    async def show_login_if_not_authenticated(self):
        if not self.reddit_service or not self.reddit_service.user:
            Logger().info("User not authenticated, showing login screen")
            await self.action_login()
        else:
            Logger().info("User is already authenticated")

    def is_authenticated(self) -> bool:
        return bool(self.reddit_service and self.reddit_service.user is not None)

    def compose(self) -> ComposeResult:
        Logger().info("Composing main UI")
        yield Header()
        with Horizontal():
            yield Sidebar(id="sidebar")
            yield PostList(id="content")
        yield Footer()

    def action_quit(self) -> None:
        Logger().debug("App quitting.")
        Logger().send_logs()
        self.exit()

    def on_key(self, event):
        Logger().info(f"Key pressed: {event.key}")
        return event

    def action_select(self) -> None:
        Logger().info("Action: select")
        if not self.is_authenticated():
            Logger().info("User not authenticated, showing login screen")
            self.call_later(self.show_login_if_not_authenticated)
            return
        post = self.query_one(PostList).get_selected_post()
        if post:
            Logger().info(f"Selected post: {getattr(post, 'title', str(post))}")
            content = self.query_one("#content")
            content.remove_children()
            content.mount(PostViewScreen(post, content, self.current_posts))

    def action_home(self) -> None:
        Logger().info("Action: home feed")
        if not self.is_authenticated():
            Logger().info("User not authenticated, showing login screen")
            self.call_later(self.show_login_if_not_authenticated)
            return
        if not self.reddit_service:
            self.notify("Reddit service not initialized", severity="error")
            return
        self.current_feed = "hot"
        posts = self.reddit_service.get_hot_posts()
        self.current_posts = posts
        self.query_one(PostList).update_posts(posts)
        self.query_one(Sidebar).update_status("Home Feed")
        self.query_one(PostList).focus()

    def action_new(self) -> None:
        Logger().info("Action: new feed")
        if not self.is_authenticated():
            Logger().info("User not authenticated, showing login screen")
            self.call_later(self.show_login_if_not_authenticated)
            return
        if not self.reddit_service:
            self.notify("Reddit service not initialized", severity="error")
            return
        self.current_feed = "new"
        posts = self.reddit_service.get_new_posts()
        self.current_posts = posts
        self.query_one(PostList).update_posts(posts)
        self.query_one(Sidebar).update_status("New Feed")
        self.query_one(PostList).focus()

    def action_top(self) -> None:
        Logger().info("Action: top feed")
        if not self.is_authenticated():
            Logger().info("User not authenticated, showing login screen")
            self.call_later(self.show_login_if_not_authenticated)
            return
        if not self.reddit_service:
            self.notify("Reddit service not initialized", severity="error")
            return
        self.current_feed = "top"
        posts = self.reddit_service.get_top_posts()
        self.current_posts = posts
        self.query_one(PostList).update_posts(posts)
        self.query_one(Sidebar).update_status("Top Feed")
        self.query_one(PostList).focus()

    async def action_search(self) -> None:
        Logger().info("Action: search")
        try:
            screen = AdvancedSearchScreen(self.query_one("#content"), self.current_posts)
            await self.push_screen(screen)
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
                Logger().info("Login successful, attempting auto-login")
                if self.reddit_service and self.reddit_service.auto_login():
                    Logger().info("Auto-login successful after manual login")
                    if self.reddit_service:
                        current_account = self.reddit_service.get_current_account()
                        if current_account:
                            self.query_one(Sidebar).update_auth_status(True, current_account)
                    self.action_home()
                else:
                    Logger().error("Failed to auto-login after manual login")
                    self.notify("Error: Failed to initialize Reddit service", severity="error")
                    self.query_one(Sidebar).update_auth_status(False)
                    # Try to show login screen again if auto-login fails
                    await self.show_login_if_not_authenticated()
            else:
                Logger().info("Login cancelled or failed")
                # If login was cancelled and user is still not authenticated, show login again
                if not self.is_authenticated():
                    self.query_one(Sidebar).update_auth_status(False)
                    await self.show_login_if_not_authenticated()
                else:
                    if self.reddit_service:
                        current_account = self.reddit_service.get_current_account()
                        if current_account:
                            self.query_one(Sidebar).update_auth_status(True, current_account)
                        self.action_home()
        except Exception as e:
            Logger().error(f"Exception in action_login: {str(e)}", exc_info=True)
            self.notify(f"Error: {str(e)}", severity="error")
            # Try to show login screen again if there was an error
            if not self.is_authenticated():
                self.query_one(Sidebar).update_auth_status(False)
                await self.show_login_if_not_authenticated()
            else:
                if self.reddit_service:
                    current_account = self.reddit_service.get_current_account()
                    if current_account:
                        self.query_one(Sidebar).update_auth_status(True, current_account)
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

            # Apply NSFW filter
            if not self.settings["show_nsfw"]:
                self.current_posts = [post for post in self.current_posts if not getattr(post, "over_18", False)]
                self.query_one(PostList).update_posts(self.current_posts)

            self.refresh()
            Logger().info("Settings applied successfully")
        except Exception as e:
            Logger().error(f"Error applying settings: {str(e)}", exc_info=True)
            self.notify("Error applying settings", severity="error")

    def get_system_commands(self, screen):
        yield from super().get_system_commands(screen)
        try:
            content = self.query_one("#content")
            children = list(content.children)
            if len(children) == 1:
                if isinstance(children[0], PostViewScreen):
                    post = children[0].post
                    yield SystemCommand("Back", "Return to post list", self.action_back)
                    if post and post.author:
                        yield SystemCommand("View User Profile", f"View profile of {post.author.name}", self.action_view_user)
                    yield SystemCommand("Save Post", "Save the currently viewed post", self.save_selected_post)
                    yield SystemCommand("Hide Post", "Hide the currently viewed post", self.hide_selected_post)
                    yield SystemCommand("Subscribe to Subreddit", f"Subscribe to r/{post.subreddit.display_name}", self.subscribe_to_subreddit)
                    yield SystemCommand("Upvote post", "Upvote the currently viewed post", self.upvote_selected_post)
                    yield SystemCommand("Downvote post", "Downvote the currently viewed post", self.downvote_selected_post)
                    yield SystemCommand("Report post", "Report the currently viewed post", self.report_selected_post)
                    yield SystemCommand("Comment on post", "Comment on the currently viewed post", self.comment_on_selected_post)
                    yield SystemCommand("Copy Post URL", "Copy the post's URL to clipboard", self.copy_post_url)
                    yield SystemCommand("Copy Post Title", "Copy the post's title to clipboard", self.copy_post_title)
                    yield SystemCommand("Open in Browser", "Open the post in your default browser", self.open_in_browser)
                    yield SystemCommand("Show QR Code", "Display QR code for the post URL", self.show_qr_code)
                    yield SystemCommand("Sort Comments: Best", "Sort comments by best", lambda: self.sort_comments("best"))
                    yield SystemCommand("Sort Comments: Top", "Sort comments by top", lambda: self.sort_comments("top"))
                    yield SystemCommand("Sort Comments: New", "Sort comments by new", lambda: self.sort_comments("new"))
                    yield SystemCommand("Sort Comments: Controversial", "Sort comments by controversial", lambda: self.sort_comments("controversial"))
                    yield SystemCommand("Sort Comments: Old", "Sort comments by old", lambda: self.sort_comments("old"))
                    yield SystemCommand("Sort Comments: Q&A", "Sort comments by Q&A", lambda: self.sort_comments("qa"))
                elif isinstance(children[0], PostList):
                    post = children[0].get_selected_post()
                    if post and post.author:
                        yield SystemCommand("View User Profile", f"View profile of {post.author.name}", self.action_view_user)
                    if post:
                        yield SystemCommand("Save Post", "Save the selected post", self.save_selected_post)
                        yield SystemCommand("Hide Post", "Hide the selected post", self.hide_selected_post)
                        yield SystemCommand("Subscribe to Subreddit", f"Subscribe to r/{post.subreddit.display_name}", self.subscribe_to_subreddit)
                        yield SystemCommand("Copy Post URL", "Copy the post's URL to clipboard", self.copy_post_url)
                        yield SystemCommand("Copy Post Title", "Copy the post's title to clipboard", self.copy_post_title)
                        yield SystemCommand("Open in Browser", "Open the post in your default browser", self.open_in_browser)
                        yield SystemCommand("Show QR Code", "Display QR code for the post URL", self.show_qr_code)
                    yield SystemCommand("Create Post", "Create a new post", self.action_create_post)
        except Exception as e:
            Logger().error(f"Error checking for PostViewScreen: {str(e)}", exc_info=True)

    def save_selected_post(self):
        try:
            if not self.reddit_service:
                self.notify("Reddit service not initialized", severity="error")
                return
                
            content = self.query_one("#content")
            children = list(content.children)
            if len(children) == 1:
                if isinstance(children[0], PostViewScreen):
                    post = children[0].post
                elif isinstance(children[0], PostList):
                    post = children[0].get_selected_post()
                else:
                    self.notify("No post selected", severity="warning")
                    return

                if post:
                    if self.reddit_service.save_post(post):
                        self.notify("Post saved successfully!", severity="information")
                        Logger().info(f"Saved post: {post.title}")
                        # Refresh the current view
                        if self.query_one(Sidebar).status == "Saved Posts":
                            posts = self.reddit_service.get_saved_posts()
                            self.current_posts = posts
                            self.query_one(PostList).update_posts(posts)
                    else:
                        self.notify("Failed to save post", severity="error")
                else:
                    self.notify("No post selected", severity="warning")
        except Exception as e:
            Logger().error(f"Error saving post: {str(e)}", exc_info=True)
            self.notify(f"Error saving post: {str(e)}", severity="error")

    def hide_selected_post(self):
        try:
            if not self.reddit_service:
                self.notify("Reddit service not initialized", severity="error")
                return
                
            content = self.query_one("#content")
            children = list(content.children)
            if len(children) == 1:
                if isinstance(children[0], PostViewScreen):
                    post = children[0].post
                elif isinstance(children[0], PostList):
                    post = children[0].get_selected_post()
                else:
                    self.notify("No post selected", severity="warning")
                    return

                if post:
                    if self.reddit_service.hide_post(post):
                        self.notify("Post hidden successfully!", severity="information")
                        Logger().info(f"Hidden post: {post.title}")
                        # Remove the post from the current list and refresh
                        if isinstance(children[0], PostList):
                            self.current_posts = [p for p in self.current_posts if p.id != post.id]
                            children[0].update_posts(self.current_posts)
                            current_status = self.query_one(Sidebar).status
                            if current_status == "Home Feed":
                                posts = self.reddit_service.get_hot_posts()
                                self.current_posts = posts
                                self.query_one(PostList).update_posts(posts)
                            elif current_status == "New Feed":
                                posts = self.reddit_service.get_new_posts()
                                self.current_posts = posts
                                self.query_one(PostList).update_posts(posts)
                            elif current_status == "Top Feed":
                                posts = self.reddit_service.get_top_posts()
                                self.current_posts = posts
                                self.query_one(PostList).update_posts(posts)
                    else:
                        self.notify("Failed to hide post", severity="error")
                else:
                    self.notify("No post selected", severity="warning")
        except Exception as e:
            Logger().error(f"Error hiding post: {str(e)}", exc_info=True)
            self.notify(f"Error hiding post: {str(e)}", severity="error")

    def subscribe_to_subreddit(self):
        try:
            if not self.reddit_service:
                self.notify("Reddit service not initialized", severity="error")
                return
                
            content = self.query_one("#content")
            children = list(content.children)
            if len(children) == 1:
                if isinstance(children[0], PostViewScreen):
                    post = children[0].post
                elif isinstance(children[0], PostList):
                    post = children[0].get_selected_post()
                else:
                    self.notify("No post selected", severity="warning")
                    return

                if post:
                    subreddit_name = post.subreddit.display_name
                    if self.reddit_service.subscribe_subreddit(subreddit_name):
                        self.notify(f"Subscribed to r/{subreddit_name}!", severity="information")
                        Logger().info(f"Subscribed to subreddit: {subreddit_name}")
                    else:
                        self.notify(f"Failed to subscribe to r/{subreddit_name}", severity="error")
                else:
                    self.notify("No post selected", severity="warning")
        except Exception as e:
            Logger().error(f"Error subscribing to subreddit: {str(e)}", exc_info=True)
            self.notify(f"Error subscribing to subreddit: {str(e)}", severity="error")

    def action_saved_posts(self) -> None:
        Logger().info("Action: saved posts")
        try:
            if not self.reddit_service or not self.reddit_service.user:
                self.notify("Please login first", severity="warning")
                return

            posts = self.reddit_service.get_saved_posts()
            self.current_posts = posts
            self.query_one(PostList).update_posts(posts)
            self.query_one(Sidebar).update_status("Saved Posts")
            self.query_one(PostList).focus()
        except Exception as e:
            Logger().error(f"Error loading saved posts: {str(e)}", exc_info=True)
            self.notify(f"Error loading saved posts: {str(e)}", severity="error")

    def action_subscribed_subreddits(self) -> None:
        Logger().info("Action: subscribed subreddits")
        try:
            if not self.reddit_service or not self.reddit_service.user:
                self.notify("Please login first", severity="warning")
                return

            content = self.query_one("#content")
            content.remove_children()
            subreddit_screen = SubredditScreen(content, self.current_posts)
            content.mount(subreddit_screen)
            subreddit_screen.focus()
            self.query_one(Sidebar).update_status("Subscribed Subreddits")
        except Exception as e:
            Logger().error(f"Error loading subscribed subreddits: {str(e)}", exc_info=True)
            self.notify(f"Error loading subscribed subreddits: {str(e)}", severity="error")

    def upvote_selected_post(self):
        post = self.query_one(PostList).get_selected_post()
        if post:
            try:
                post.upvote()
                self.notify("Upvoted post!", severity="information")
                Logger().info(f"Upvoted post: {getattr(post, 'title', str(post))}")
            except Exception as e:
                Logger().error(f"Error upvoting post: {str(e)}", exc_info=True)
                self.notify(f"Error upvoting post: {str(e)}", severity="error")
        else:
            self.notify("No post selected", severity="warning")

    def downvote_selected_post(self):
        post = self.query_one(PostList).get_selected_post()
        if post:
            try:
                post.downvote()
                self.notify("Downvoted post!", severity="information")
                Logger().info(f"Downvoted post: {getattr(post, 'title', str(post))}")
            except Exception as e:
                Logger().error(f"Error downvoting post: {str(e)}", exc_info=True)
                self.notify(f"Error downvoting post: {str(e)}", severity="error")
        else:
            self.notify("No post selected", severity="warning")

    async def report_selected_post(self):
        post = self.query_one(PostList).get_selected_post()
        if not post:
            self.notify("No post selected", severity="warning")
            return
        reasons = [
            "Spam",
            "Vote Manipulation",
            "Personal Information",
            "Sexualizing Minors",
            "Breaking Reddit",
            "Other"
        ]
        reason = await self.push_screen(ReportReasonScreen(reasons))
        if reason and reason != "back":
            try:
                post.report(reason)
                self.notify(f"Reported post for: {reason}", severity="warning")
                Logger().info(f"Reported post: {getattr(post, 'title', str(post))} for {reason}")
            except Exception as e:
                Logger().error(f"Error reporting post: {str(e)}", exc_info=True)
                self.notify(f"Error reporting post: {str(e)}", severity="error")
        elif reason == "back":
            self.notify("Report cancelled", severity="information")

    def comment_on_selected_post(self):
        post = self.query_one(PostList).get_selected_post()
        if post:
            self.logger.info(f"Opening comment screen for post: {getattr(post, 'title', str(post))}")
            self.push_screen(CommentScreen(post))
        else:
            self.notify("No post selected", severity="warning")

    def action_view_user(self) -> None:
        Logger().info("Action: view user")
        try:
            content = self.query_one("#content")
            children = list(content.children)
            if len(children) == 1:
                if isinstance(children[0], PostList):
                    post = children[0].get_selected_post()
                elif isinstance(children[0], PostViewScreen):
                    post = children[0].post
                else:
                    self.notify("Please select a post first", severity="warning")
                    return

                if post and post.author:
                    username = post.author.name
                    content.remove_children()
                    user_screen = UserProfileScreen(username, content, self.current_posts)
                    content.mount(user_screen)
                    user_screen.focus()
                    self.query_one(Sidebar).update_status(f"User Profile: {username}")
                else:
                    self.notify("No user selected", severity="warning")
            else:
                self.notify("Please select a post first", severity="warning")
        except Exception as e:
            Logger().error(f"Error viewing user profile: {str(e)}", exc_info=True)
            self.notify(f"Error viewing user profile: {str(e)}", severity="error")

    def action_my_profile(self) -> None:
        Logger().info("Action: my profile")
        try:
            if not self.reddit_service or not self.reddit_service.user:
                self.notify("Please login first", severity="warning")
                return

            content = self.query_one("#content")
            content.remove_children()
            user_screen = UserProfileScreen(self.reddit_service.user, content, self.current_posts)
            content.mount(user_screen)
            user_screen.focus()
            self.query_one(Sidebar).update_status(f"User Profile: {self.reddit_service.user}")
        except Exception as e:
            Logger().error(f"Error viewing own profile: {str(e)}", exc_info=True)
            self.notify(f"Error viewing profile: {str(e)}", severity="error")

    def copy_post_url(self):
        try:
            content = self.query_one("#content")
            children = list(content.children)
            if len(children) == 1:
                if isinstance(children[0], PostViewScreen):
                    post = children[0].post
                elif isinstance(children[0], PostList):
                    post = children[0].get_selected_post()
                else:
                    self.notify("No post selected", severity="warning")
                    return

                if post:
                    import pyperclip
                    url = f"https://reddit.com{post.permalink}"
                    pyperclip.copy(url)
                    self.notify("Post URL copied to clipboard!", severity="information")
                    Logger().info(f"Copied post URL: {url}")
                else:
                    self.notify("No post selected", severity="warning")
        except Exception as e:
            Logger().error(f"Error copying post URL: {str(e)}", exc_info=True)
            self.notify(f"Error copying URL: {str(e)}", severity="error")

    def copy_post_title(self):
        try:
            content = self.query_one("#content")
            children = list(content.children)
            if len(children) == 1:
                if isinstance(children[0], PostViewScreen):
                    post = children[0].post
                elif isinstance(children[0], PostList):
                    post = children[0].get_selected_post()
                else:
                    self.notify("No post selected", severity="warning")
                    return

                if post:
                    import pyperclip
                    title = post.title
                    pyperclip.copy(title)
                    self.notify("Post title copied to clipboard!", severity="information")
                    Logger().info(f"Copied post title: {title}")
                else:
                    self.notify("No post selected", severity="warning")
        except Exception as e:
            Logger().error(f"Error copying post title: {str(e)}", exc_info=True)
            self.notify(f"Error copying title: {str(e)}", severity="error")

    def open_in_browser(self):
        try:
            content = self.query_one("#content")
            children = list(content.children)
            if len(children) == 1:
                if isinstance(children[0], PostViewScreen):
                    post = children[0].post
                elif isinstance(children[0], PostList):
                    post = children[0].get_selected_post()
                else:
                    self.notify("No post selected", severity="warning")
                    return

                if post:
                    import webbrowser
                    url = f"https://reddit.com{post.permalink}"
                    webbrowser.open(url)
                    self.notify("Opening post in browser...", severity="information")
                    Logger().info(f"Opening post in browser: {url}")
                else:
                    self.notify("No post selected", severity="warning")
        except Exception as e:
            Logger().error(f"Error opening post in browser: {str(e)}", exc_info=True)
            self.notify(f"Error opening in browser: {str(e)}", severity="error")

    async def show_qr_code(self):
        try:
            content = self.query_one("#content")
            children = list(content.children)
            if len(children) == 1:
                if isinstance(children[0], PostViewScreen):
                    post = children[0].post
                elif isinstance(children[0], PostList):
                    post = children[0].get_selected_post()
                else:
                    self.notify("No post selected", severity="warning")
                    return

                if post:
                    url = f"https://reddit.com{post.permalink}"
                    qr_screen = QRScreen(url)
                    await self.push_screen(qr_screen)
                    Logger().info(f"Showing QR code for URL: {url}")
                else:
                    self.notify("No post selected", severity="warning")
        except Exception as e:
            Logger().error(f"Error showing QR code: {str(e)}", exc_info=True)
            self.notify(f"Error showing QR code: {str(e)}", severity="error")

    async def action_advanced_search(self) -> None:
        self.logger.info("Action: advanced search")
        screen = AdvancedSearchScreen(self.query_one("#content"), self.current_posts)
        await self.push_screen(screen)

    def sort_comments(self, sort_mode):
        try:
            content = self.query_one("#content")
            children = list(content.children)
            if len(children) == 1 and isinstance(children[0], PostViewScreen):
                children[0].sort_comments(sort_mode)
                self.notify(f"Comments sorted by {sort_mode}", severity="information")
        except Exception as e:
            Logger().error(f"Error sorting comments: {str(e)}", exc_info=True)
            self.notify(f"Error sorting comments: {str(e)}", severity="error")

    def action_back(self):
        try:
            content = self.query_one("#content")
            children = list(content.children)
            if len(children) == 1 and isinstance(children[0], PostViewScreen):
                content.remove_children()
                post_list = PostList(posts=self.current_posts, id="content")
                content.mount(post_list)
                post_list.focus()
                Logger().info("Returned to post list")
        except Exception as e:
            Logger().error(f"Error returning to post list: {str(e)}", exc_info=True)
            self.notify(f"Error returning to post list: {str(e)}", severity="error")

    async def action_create_post(self) -> None:
        self.logger.info("Action: create post")
        try:
            content = self.query_one("#content")
            children = list(content.children)
            subreddit = None
            if len(children) == 1:
                if isinstance(children[0], PostList):
                    post = children[0].get_selected_post()
                    if post:
                        subreddit = post.subreddit.display_name
            content.remove_children()
            screen = PostCreationScreen(subreddit)
            screen.focus()
            self.query_one(Sidebar).update_status("Create Post")
        except Exception as e:
            self.logger.error(f"Error creating post: {str(e)}", exc_info=True)
            self.notify(f"Error creating post: {str(e)}", severity="error")

    async def action_credits(self) -> None:
        """Show credits screen."""
        Logger().info("Action: credits")
        await self.push_screen(CreditsScreen())

    async def action_rate_limit(self) -> None:
        Logger().info("Action: rate limit info")
        try:
            if not self.reddit_service or not self.reddit_service.reddit:
                self.notify("Please login first", severity="warning")
                return

            content = self.query_one("#content")
            content.remove_children()
            rate_limit_screen = RateLimitScreen(self.reddit_service)
            content.mount(rate_limit_screen)
            rate_limit_screen.focus()
            self.query_one(Sidebar).update_status("Rate Limit Information")
        except Exception as e:
            Logger().error(f"Error showing rate limit screen: {str(e)}", exc_info=True)
            self.notify(f"Error showing rate limit info: {str(e)}", severity="error")

    async def action_create_theme(self) -> None:
        Logger().info("Action: create theme")
        try:
            content = self.query_one("#content")
            content.remove_children()
            screen = ThemeCreationScreen(content, self.current_posts)
            content.mount(screen)
            screen.focus()
            self.query_one(Sidebar).update_status("Create Theme")
        except Exception as e:
            Logger().error(f"Error creating theme: {str(e)}", exc_info=True)
            self.notify(f"Error creating theme: {str(e)}", severity="error")

    async def action_messages(self) -> None:
        Logger().info("Action: messages")
        try:
            if not self.reddit_service or not self.reddit_service.user:
                self.notify("Please login first", severity="warning")
                return

            content = self.query_one("#content")
            parent = content.parent
            content.remove()
            self.call_later(self._mount_messages_screen, parent)
            self.query_one(Sidebar).update_status("Messages")
        except Exception as e:
            Logger().error(f"Error showing messages screen: {str(e)}", exc_info=True)
            self.notify(f"Error showing messages: {str(e)}", severity="error")

    async def _mount_messages_screen(self, parent):
        from textual.containers import Container
        from components.messages_screen import MessagesScreen
        new_content = Container(id="content")
        parent.mount(new_content)
        new_content.mount(MessagesScreen(self.reddit_service))

    async def action_account_management(self) -> None:
        Logger().info("Action: account management")
        try:
            if not self.reddit_service:
                self.notify("Please login first", severity="warning")
                return

            content = self.query_one("#content")
            if content.query("#account_management_wrapper"):
                return

            content.remove_children()
            account_widget = AccountManagementWidget(self.reddit_service)
            content.mount(Container(account_widget, id="account_management_wrapper"))
            account_widget.focus()
            self.query_one(Sidebar).update_status("Account Management")
        except Exception as e:
            Logger().error(f"Error in account management: {str(e)}", exc_info=True)
            self.notify(f"Error: {str(e)}", severity="error")

    def on_account_management_widget_account_switched(self, message: AccountManagementWidget.AccountSwitched):
        account = message.username
        if account:
            Logger().info(f"Account switched to: {account}, reloading current feed")
            
            content = self.query_one("#content")
            content.remove_children()

            if self.current_feed == "hot":
                self.action_home()
            elif self.current_feed == "new":
                self.action_new()
            elif self.current_feed == "top":
                self.action_top()
            else:
                self.action_home()

    def on_account_management_widget_back_requested(self, message: AccountManagementWidget.BackRequested):
        content = self.query_one("#content")
        content.remove_children()
        content.focus()
        
        status = "Home Feed"
        if self.current_feed == "new":
            status = "New Feed"
        elif self.current_feed == "top":
            status = "Top Feed"
        
        self.query_one(Sidebar).update_status(status)

    async def action_subreddit_management(self) -> None:
        Logger().info("Action: subreddit management")
        try:
            if not self.reddit_service or not self.reddit_service.user:
                self.notify("Please login first", severity="warning")
                return

            content = self.query_one("#content")
            content.remove_children()
            subreddit_screen = SubredditManagementScreen(self.reddit_service)
            content.mount(subreddit_screen)
            subreddit_screen.focus()
            self.query_one(Sidebar).update_status("Subreddit Management")
        except Exception as e:
            Logger().error(f"Error in subreddit management: {str(e)}", exc_info=True)
            self.notify(f"Error: {str(e)}", severity="error")

    async def action_search_subreddits(self) -> None:
        Logger().info("Action: search subreddits")
        try:
            if not self.reddit_service or not self.reddit_service.user:
                self.notify("Please login first", severity="warning")
                return

            screen = AdvancedSearchScreen(self.query_one("#content"), self.current_posts)
            await self.push_screen(screen)
            self.query_one(Sidebar).update_status("Subreddit Search")
        except Exception as e:
            Logger().error(f"Error searching subreddits: {str(e)}", exc_info=True)
            self.notify(f"Error: {str(e)}", severity="error")

    async def action_search_users(self) -> None:
        Logger().info("Action: search users")
        try:
            if not self.reddit_service or not self.reddit_service.user:
                self.notify("Please login first", severity="warning")
                return

            screen = AdvancedSearchScreen(self.query_one("#content"), self.current_posts)
            await self.push_screen(screen)
            self.query_one(Sidebar).update_status("User Search")
        except Exception as e:
            Logger().error(f"Error searching users: {str(e)}", exc_info=True)
            self.notify(f"Error: {str(e)}", severity="error")

if __name__ == "__main__":
    if os.path.exists("log_sending.permission.jhna"):
        with open("log_sending.permission.jhna", "r") as f:
            data = json.load(f)
            if data["log_sending"] == "true":
                Logger().send_logs_to_developer = True
            else:
                Logger().info("Logs will not be sent to the developer.")
    else:
        print("Before starting RedditTUI, we need to set up the logger.")
        print("RedditTUI will always log to a file.")
        print("Any Crash or Exception will be logged and anonimously sent to the developer for debugging purposes.")

        a = input("Do you also want to send every other log anonimously to the developer for debugging purposes? (y/n): ")
        if a.lower() == "y":
            Logger().send_logs_to_developer = True
            soption = True
        else:
            Logger().info("Logs will not be sent to the developer.")
            soption = False
        if soption:
            a = input("Remember choice? (y/n): ")
            if a.lower() == "y":
                with open("log_sending.permission.jhna", "w") as f:
                    if soption == True:
                        f.write('{"log_sending": true}')
                    else:
                        f.write('{"log_sending": false}')
    Logger().info(f"=============================================================== Starting RedditTUI app at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ================================================================")
    app = RedditTUI()
    try:
        app.run()
    except Exception as e:
        Logger().error("Unhandled exception occurred", exc_info=True)
        Logger().send_crash_report(type(e), e, e.__traceback__)
        raise
    finally:
        Logger().send_logs()
        Logger().info(f"=============================================================== RedditTUI app exited at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ================================================================")