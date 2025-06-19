from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Input, Button, Static, Select, DataTable
from textual.screen import ModalScreen
from utils.logger import Logger
from services.reddit_service import RedditService
from rich.text import Text
from datetime import datetime

class SubredditManagementScreen(ModalScreen):
    def __init__(self, reddit_service: RedditService):
        super().__init__()
        self.reddit_service = reddit_service
        self.logger = Logger()
        self.subreddits = []
        self.search_query = ""
        self.current_view = "subscribed"
        self.selected_subreddit = None
        
        self.view_options = [
            ("Subscribed", "subscribed"),
            ("Popular", "popular"),
            ("New", "new"),
            ("Trending", "trending"),
            ("Search", "search")
        ]

    def compose(self) -> ComposeResult:
        self.logger.info("Composing SubredditManagementScreen UI")
        yield Container(
            Vertical(
                Static("Subreddit Management", classes="title"),
                Horizontal(
                    Select(self.view_options, id="view_select", prompt="View", classes="wide_select"),
                    Input(placeholder="Search subreddits...", id="search_input", classes="wide_input"),
                    Button("Search", id="search_button", classes="search_btn"),
                    id="controls"
                ),
                DataTable(id="subreddits_table"),
                Horizontal(
                    Button("Subscribe", id="subscribe_button", classes="action_btn"),
                    Button("Unsubscribe", id="unsubscribe_button", classes="action_btn"),
                    Button("View Posts", id="view_posts_button", classes="action_btn"),
                    Button("Close", id="close_button", classes="action_btn"),
                    id="actions"
                ),
                id="subreddit_container"
            ),
            id="subreddit_management_container"
        )

    def on_mount(self):
        self.logger.info("SubredditManagementScreen mounted")
        self.table = self.query_one("#subreddits_table", DataTable)
        self.table.add_columns("Name", "Title", "Subscribers", "Active", "NSFW", "Created")
        self.load_subreddits()

    def on_select_changed(self, event: Select.Changed) -> None:
        self.logger.info(f"View changed: {event.value}")
        self.current_view = event.value
        self.load_subreddits()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.logger.info(f"Search submitted: {event.value}")
        self.search_query = event.value
        if self.current_view == "search":
            self.search_subreddits()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.logger.info(f"Button pressed: {event.button.id}")
        if event.button.id == "search_button":
            self.search_subreddits()
        elif event.button.id == "subscribe_button":
            self.subscribe_to_selected()
        elif event.button.id == "unsubscribe_button":
            self.unsubscribe_from_selected()
        elif event.button.id == "view_posts_button":
            self.view_posts_of_selected()
        elif event.button.id == "close_button":
            self.dismiss()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.logger.info(f"Row selected: {event.row_key}")
        self.selected_subreddit = event.row_key

    def load_subreddits(self):
        """Load subreddits based on current view."""
        try:
            if self.current_view == "subscribed":
                self.subreddits = self.reddit_service.get_subscribed_subreddits()
            elif self.current_view == "popular":
                self.subreddits = self.reddit_service.get_popular_subreddits()
            elif self.current_view == "new":
                self.subreddits = self.reddit_service.get_new_subreddits()
            elif self.current_view == "trending":
                self.subreddits = self.reddit_service.get_trending_subreddits()
            elif self.current_view == "search":
                if self.search_query:
                    self.search_subreddits()
                return
            
            self.update_table()
        except Exception as e:
            self.logger.error(f"Error loading subreddits: {str(e)}", exc_info=True)
            self.notify(f"Error loading subreddits: {str(e)}", severity="error")

    def search_subreddits(self):
        """Search for subreddits."""
        try:
            if not self.search_query:
                self.notify("Please enter a search query", severity="warning")
                return
            
            self.subreddits = self.reddit_service.search_subreddits(self.search_query)
            self.update_table()
        except Exception as e:
            self.logger.error(f"Error searching subreddits: {str(e)}", exc_info=True)
            self.notify(f"Error searching subreddits: {str(e)}", severity="error")

    def update_table(self):
        """Update the subreddits table."""
        self.table.clear()
        
        for subreddit in self.subreddits:
            try:
                name = subreddit.display_name
                title = subreddit.title[:50] + "..." if len(subreddit.title) > 50 else subreddit.title
                subscribers = f"{subreddit.subscribers:,}" if hasattr(subreddit, 'subscribers') else "N/A"
                active = f"{subreddit.active_user_count:,}" if hasattr(subreddit, 'active_user_count') else "N/A"
                nsfw = "Yes" if getattr(subreddit, 'over18', False) else "No"
                created = datetime.fromtimestamp(subreddit.created_utc).strftime("%Y-%m-%d") if hasattr(subreddit, 'created_utc') else "N/A"
                
                self.table.add_row(name, title, subscribers, active, nsfw, created, key=name)
            except Exception as e:
                self.logger.error(f"Error adding subreddit to table: {str(e)}", exc_info=True)

    def subscribe_to_selected(self):
        """Subscribe to the selected subreddit."""
        if not self.selected_subreddit:
            self.notify("Please select a subreddit first", severity="warning")
            return
        
        try:
            subreddit_name = str(self.selected_subreddit)
            if self.reddit_service.subscribe_subreddit(subreddit_name):
                self.notify(f"Subscribed to r/{subreddit_name}", severity="information")
                self.load_subreddits()
            else:
                self.notify(f"Failed to subscribe to r/{subreddit_name}", severity="error")
        except Exception as e:
            self.logger.error(f"Error subscribing to subreddit: {str(e)}", exc_info=True)
            self.notify(f"Error subscribing: {str(e)}", severity="error")

    def unsubscribe_from_selected(self):
        """Unsubscribe from the selected subreddit."""
        if not self.selected_subreddit:
            self.notify("Please select a subreddit first", severity="warning")
            return
        
        try:
            subreddit_name = str(self.selected_subreddit)
            if self.reddit_service.unsubscribe_subreddit(subreddit_name):
                self.notify(f"Unsubscribed from r/{subreddit_name}", severity="information")
                self.load_subreddits()
            else:
                self.notify(f"Failed to unsubscribe from r/{subreddit_name}", severity="error")
        except Exception as e:
            self.logger.error(f"Error unsubscribing from subreddit: {str(e)}", exc_info=True)
            self.notify(f"Error unsubscribing: {str(e)}", severity="error")

    def view_posts_of_selected(self):
        """View posts from the selected subreddit."""
        if not self.selected_subreddit:
            self.notify("Please select a subreddit first", severity="warning")
            return
        
        try:
            subreddit_name = str(self.selected_subreddit)
            posts = self.reddit_service.get_subreddit_posts(subreddit_name)
            if posts:
                self.dismiss({"action": "view_posts", "subreddit": subreddit_name, "posts": posts})
            else:
                self.notify(f"No posts found in r/{subreddit_name}", severity="warning")
        except Exception as e:
            self.logger.error(f"Error getting posts from subreddit: {str(e)}", exc_info=True)
            self.notify(f"Error getting posts: {str(e)}", severity="error") 