from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Input, Button, Static, Select
from textual.widget import Widget
from utils.logger import Logger
from services.reddit_service import RedditService
from components.post_list import PostList
from rich.text import Text

class SearchScreen(Widget):
    def __init__(self, parent_content, posts):
        super().__init__()
        self.parent_content = parent_content
        self.posts = posts
        self.logger = Logger()
        self.reddit_service = None
        self.search_query = ""
        self.search_results = []
        self.search_type = "relevance"
        self.time_filter = "all"
        self.sort_options = [
            ("relevance", "Relevance"),
            ("hot", "Hot"),
            ("top", "Top"),
            ("new", "New"),
            ("comments", "Most Comments")
        ]
        self.time_options = [
            ("all", "All Time"),
            ("hour", "Past Hour"),
            ("day", "Past 24 Hours"),
            ("week", "Past Week"),
            ("month", "Past Month"),
            ("year", "Past Year")
        ]

    def compose(self) -> ComposeResult:
        self.logger.info("Composing SearchScreen UI")
        yield Container(
            Vertical(
                Static("Search Reddit", classes="title"),
                Input(placeholder="Enter search query", id="search_input"),
                Horizontal(
                    Select(
                        self.sort_options,
                        id="sort_select",
                        prompt="Sort by"
                    ),
                    Select(
                        self.time_options,
                        id="time_select",
                        prompt="Time"
                    ),
                    id="search_filters"
                ),
                Button("Search", id="search_button"),
                id="search_form"
            ),
            id="search_container"
        )

    def on_mount(self):
        self.logger.info("SearchScreen mounted")
        self.reddit_service = self.app.reddit_service
        self.query_one("#search_input").focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.logger.info(f"Search input submitted: {event.value}")
        self.search_query = event.value
        self.perform_search()

    def on_select_changed(self, event: Select.Changed) -> None:
        self.logger.info(f"Select changed: {event.select.id} = {event.value}")
        if event.select.id == "sort_select":
            selected_option = next((opt for opt in self.sort_options if opt[1] == event.value), None)
            if selected_option:
                self.search_type = selected_option[0]
        elif event.select.id == "time_select":
            selected_option = next((opt for opt in self.time_options if opt[1] == event.value), None)
            if selected_option:
                self.time_filter = selected_option[0]

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.logger.info(f"Button pressed: {event.button.id}")
        if event.button.id == "search_button":
            self.search_query = self.query_one("#search_input").value
            self.perform_search()

    def get_search_header(self):
        sort_display = next((opt[1] for opt in self.sort_options if opt[0] == self.search_type), self.search_type)
        time_display = next((opt[1] for opt in self.time_options if opt[0] == self.time_filter), self.time_filter)
        
        header = Text()
        header.append("Search Results for: ", style="bold blue")
        header.append(f'"{self.search_query}"', style="bold white")
        header.append("\nSort: ", style="bold blue")
        header.append(sort_display, style="white")
        header.append(" | Time: ", style="bold blue")
        header.append(time_display, style="white")
        header.append("\n\n", style="white")
        header.append("This feature is still in development and may not work yet. Please report any issues to me via slack :D.", style="bold white")
        return header

    def perform_search(self):
        if not self.search_query:
            self.logger.warning("Empty search query")
            self.notify("Please enter a search query", severity="error")
            return

        self.logger.info(f"Performing search for: {self.search_query} (type: {self.search_type}, time: {self.time_filter})")
        try:
            if not self.reddit_service:
                self.logger.error("RedditService not initialized")
                self.notify("Error: Reddit service not initialized", severity="error")
                return

            self.search_results = self.reddit_service.search_posts(
                self.search_query,
                sort=self.search_type,
                time_filter=self.time_filter
            )
            self.logger.info(f"Found {len(self.search_results)} search results")

            if not self.search_results:
                self.notify("No results found", severity="warning")
                return

            self.parent_content.remove_children()
            container = Vertical(id="content")
            self.parent_content.mount(container)
            
            header = Static(self.get_search_header(), id="search_header")
            post_list = PostList(posts=self.search_results, id="post_list")
            
            container.mount(header)
            container.mount(post_list)
            
            self.app.active_widget = "content"
            post_list.focus()

        except Exception as e:
            self.logger.error(f"Error performing search: {str(e)}", exc_info=True)
            self.notify(f"Error performing search: {str(e)}", severity="error") 