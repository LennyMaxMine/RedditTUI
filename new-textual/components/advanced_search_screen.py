from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Input, Button, Static, Select, Switch
from textual.screen import ModalScreen
from utils.logger import Logger
from services.reddit_service import RedditService
from components.post_list import PostList
from rich.text import Text
from components.sidebar import Sidebar

class AdvancedSearchScreen(ModalScreen):
    def __init__(self, parent_content, posts):
        super().__init__()
        self.parent_content = parent_content
        self.posts = posts
        self.logger = Logger()
        self.reddit_service = None
        self.search_query = ""
        self.search_results = []
        
        # Search parameters
        self.sort_options = [
            ("Relevance", "relevance"),
            ("Hot", "hot"),
            ("Top", "top"),
            ("New", "new"),
            ("Most Comments", "comments")
        ]
        
        self.time_options = [
            ("All Time", "all"),
            ("Past Hour", "hour"),
            ("Past 24 Hours", "day"),
            ("Past Week", "week"),
            ("Past Month", "month"),
            ("Past Year", "year")
        ]
        
        self.type_options = [
            ("All Types", "all"),
            ("Links Only", "link"),
            ("Text Posts Only", "self"),
            ("Images Only", "image"),
            ("Videos Only", "video")
        ]
        
        self.subreddit_filter = ""
        self.author_filter = ""
        self.score_filter = ""
        self.comments_filter = ""
        self.include_nsfw = False
        self.include_spoilers = False
        self.include_archived = False
        self.include_locked = False

    def compose(self) -> ComposeResult:
        self.logger.info("Composing AdvancedSearchScreen UI")
        yield Container(
            Vertical(
                Static("Advanced Search", classes="title"),
                Input(placeholder="Search query", id="search_input", classes="wide_input"),
                Static("Filters", classes="section_title distinct_title"),
                Horizontal(
                    Select(self.sort_options, id="sort_select", prompt="Sort by", classes="wide_select"),
                    Select(self.time_options, id="time_select", prompt="Time", classes="wide_select"),
                    Select(self.type_options, id="type_select", prompt="Type", classes="wide_select"),
                    id="main_filters"
                ),
                Horizontal(
                    Vertical(
                        Static("Subreddit Filter:", classes="filter_label"),
                        Input(placeholder="e.g., programming+python", id="subreddit_filter", classes="wide_input"),
                    ),
                    Vertical(
                        Static("Author Filter:", classes="filter_label"),
                        Input(placeholder="e.g., username", id="author_filter", classes="wide_input"),
                    ),
                    id="filter_row1"
                ),
                Horizontal(
                    Vertical(
                        Static("Score Filter:", classes="filter_label"),
                        Input(placeholder="e.g., >100", id="score_filter", classes="wide_input"),
                    ),
                    Vertical(
                        Static("Comments Filter:", classes="filter_label"),
                        Input(placeholder="e.g., >10", id="comments_filter", classes="wide_input"),
                    ),
                    id="filter_row2"
                ),
                Static("Additional Options", classes="section_title distinct_title"),
                Horizontal(
                    Vertical(
                        Static("Include NSFW:", classes="switch_label"),
                        Switch(id="include_nsfw", classes="adv_switch"),
                    ),
                    Vertical(
                        Static("Include Spoilers:", classes="switch_label"),
                        Switch(id="include_spoilers", classes="adv_switch"),
                    ),
                    Vertical(
                        Static("Include Archived:", classes="switch_label"),
                        Switch(id="include_archived", classes="adv_switch"),
                    ),
                    Vertical(
                        Static("Include Locked:", classes="switch_label"),
                        Switch(id="include_locked", classes="adv_switch"),
                    ),
                    id="additional_options"
                ),
                Horizontal(
                    Button("Search", id="search_button", classes="search_btn"),
                    Button("Cancel", id="cancel_button", classes="search_btn"),
                    id="button_container"
                ),
                id="search_form"
            ),
            id="search_container"
        )

    def on_mount(self):
        self.logger.info("AdvancedSearchScreen mounted")
        self.reddit_service = self.app.reddit_service
        self.query_one("#search_input").focus()
        self.app.query_one(Sidebar).update_status("Advanced Search")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.logger.info(f"Search input submitted: {event.value}")
        self.search_query = event.value
        self.perform_search()

    def on_select_changed(self, event: Select.Changed) -> None:
        self.logger.info(f"Select changed: {event.select.id} = {event.value}")

    def on_switch_changed(self, event: Switch.Changed) -> None:
        self.logger.info(f"Switch changed: {event.switch.id} = {event.value}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.logger.info(f"Button pressed: {event.button.id}")
        if event.button.id == "search_button":
            self.collect_search_params()
            self.perform_search()
        elif event.button.id == "cancel_button":
            self.dismiss()

    def collect_search_params(self):
        self.search_query = self.query_one("#search_input").value
        self.subreddit_filter = self.query_one("#subreddit_filter").value
        self.author_filter = self.query_one("#author_filter").value
        self.score_filter = self.query_one("#score_filter").value
        self.comments_filter = self.query_one("#comments_filter").value
        self.include_nsfw = self.query_one("#include_nsfw").value
        self.include_spoilers = self.query_one("#include_spoilers").value
        self.include_archived = self.query_one("#include_archived").value
        self.include_locked = self.query_one("#include_locked").value

    def build_search_query(self):
        query_parts = [self.search_query]
        
        if self.subreddit_filter:
            query_parts.append(f"subreddit:{self.subreddit_filter}")
        if self.author_filter:
            query_parts.append(f"author:{self.author_filter}")
        if self.score_filter:
            query_parts.append(f"score:{self.score_filter}")
        if self.comments_filter:
            query_parts.append(f"num_comments:{self.comments_filter}")
            
        if not self.include_nsfw:
            query_parts.append("nsfw:no")
        if not self.include_spoilers:
            query_parts.append("spoiler:no")
        if not self.include_archived:
            query_parts.append("archived:no")
        if not self.include_locked:
            query_parts.append("locked:no")
            
        return " ".join(query_parts)

    def get_select_value(self, select_widget, default):
        value = select_widget.value
        if value in (None, "", Select.BLANK):
            return default
        return value

    def perform_search(self):
        if not self.search_query:
            self.logger.warning("Empty search query")
            self.notify("Please enter a search query", severity="error")
            return

        self.logger.info("Performing advanced search")
        try:
            if not self.reddit_service:
                self.logger.error("RedditService not initialized")
                self.notify("Error: Reddit service not initialized", severity="error")
                return

            full_query = self.build_search_query()
            self.logger.info(f"Full search query: {full_query}")

            sort_value = self.get_select_value(self.query_one("#sort_select"), "relevance")
            time_value = self.get_select_value(self.query_one("#time_select"), "all")
            type_value = self.get_select_value(self.query_one("#type_select"), "all")

            self.search_results = self.reddit_service.search_posts(
                full_query,
                sort=sort_value,
                time_filter=time_value
            )
            self.logger.info(f"Found {len(self.search_results)} search results")

            if not self.search_results:
                self.notify("No results found", severity="warning")
                return

            self.parent_content.remove_children()
            header = Static(self.get_search_header(sort_value, time_value, type_value), id="search_header")
            post_list = PostList(posts=self.search_results, id="content")
            self.parent_content.mount(header)
            self.parent_content.mount(post_list)
            self.app.active_widget = "content"
            post_list.focus()
            self.app.query_one(Sidebar).update_status("Advanced Search Results")
            self.dismiss()

        except Exception as e:
            self.logger.error(f"Error performing search: {str(e)}", exc_info=True)
            self.notify(f"Error performing search: {str(e)}", severity="error")

    def get_search_header(self, sort_value=None, time_value=None, type_value=None):
        if sort_value is None:
            sort_value = self.get_select_value(self.query_one("#sort_select"), "relevance")
        if time_value is None:
            time_value = self.get_select_value(self.query_one("#time_select"), "all")
        if type_value is None:
            type_value = self.get_select_value(self.query_one("#type_select"), "all")

        sort_display = next((opt[0] for opt in self.sort_options if opt[1] == sort_value), "Relevance")
        time_display = next((opt[0] for opt in self.time_options if opt[1] == time_value), "All Time")
        type_display = next((opt[0] for opt in self.type_options if opt[1] == type_value), "All Types")
        
        header = Text()
        header.append("Advanced Search Results\n\n", style="bold blue")
        header.append(f"Query: {self.search_query}\n", style="white")
        header.append(f"Sort: {sort_display} | Time: {time_display} | Type: {type_display}\n", style="white")
        
        if self.subreddit_filter:
            header.append(f"Subreddit: {self.subreddit_filter}\n", style="white")
        if self.author_filter:
            header.append(f"Author: {self.author_filter}\n", style="white")
        if self.score_filter:
            header.append(f"Score: {self.score_filter}\n", style="white")
        if self.comments_filter:
            header.append(f"Comments: {self.comments_filter}\n", style="white")
            
        header.append("\n", style="white")
        return header 