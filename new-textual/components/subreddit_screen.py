from textual.app import ComposeResult
from textual.containers import Container, Vertical, ScrollableContainer
from textual.widgets import Static
from textual.widget import Widget
from textual.reactive import reactive
from textual.binding import Binding
from textual.message import Message
from utils.logger import Logger
from services.reddit_service import RedditService
from rich.text import Text
from components.post_list import PostList

class SubredditList(Widget):
    class SubredditSelected(Message):
        def __init__(self, sender):
            super().__init__()
            self.sender = sender

    BINDINGS = [
        Binding("up", "cursor_up", "Up", show=True),
        Binding("down", "cursor_down", "Down", show=True),
        Binding("enter", "select", "Select", show=True),
    ]
    selected_index = reactive(0)
    def __init__(self, subreddits=None, id=None):
        super().__init__(id=id)
        self.subreddits = subreddits or []
        self.can_focus = True

    def update_subreddits(self, subreddits):
        self.subreddits = subreddits
        self.selected_index = 0
        self.refresh()

    def render(self):
        if not self.subreddits:
            return Text("No subreddits found")
        content = []
        for i, subreddit in enumerate(self.subreddits):
            prefix = "▶ " if i == self.selected_index else "  "
            name = f"r/{subreddit.display_name}"
            subs = f"👥 {subreddit.subscribers:,}"
            desc = subreddit.public_description or subreddit.description or "No description"
            desc = desc[:80] + ("..." if len(desc) > 80 else "")
            line = Text()
            line.append(prefix, "bold blue" if i == self.selected_index else "white")
            line.append(name, "bold white" if i == self.selected_index else "white")
            line.append(f" | {subs}\n", "green")
            line.append(f"    {desc}\n", "white")
            content.append(line)
        return Text.assemble(*content)

    def action_cursor_up(self):
        if self.selected_index > 0:
            self.selected_index -= 1
            self.refresh()
            self.scroll_visible()

    def action_cursor_down(self):
        if self.selected_index < len(self.subreddits) - 1:
            self.selected_index += 1
            self.refresh()
            self.scroll_visible()

    def scroll_visible(self):
        parent = self.parent
        if parent and hasattr(parent, "scroll_to"):
            parent.scroll_to(self.selected_index * 4)

    def action_select(self):
        self.post_message(self.SubredditSelected(self))

    def get_selected_subreddit(self):
        if 0 <= self.selected_index < len(self.subreddits):
            return self.subreddits[self.selected_index]
        return None

class SubredditScreen(Widget):
    def __init__(self, parent_content, posts):
        super().__init__()
        self.parent_content = parent_content
        self.posts = posts
        self.logger = Logger()
        self.reddit_service = None
        self.subreddits = []

    def compose(self) -> ComposeResult:
        self.logger.info("Composing SubredditScreen UI")
        yield Container(
            Vertical(
                Static("Subscribed Subreddits", classes="title"),
                ScrollableContainer(
                    SubredditList(id="subreddit_list"),
                    id="subreddit_scroll"
                ),
                id="subreddit_container"
            ),
            id="main_container"
        )

    def on_mount(self):
        self.logger.info("SubredditScreen mounted")
        self.reddit_service = self.app.reddit_service
        self.fetch_subreddits()
        self.query_one("#subreddit_list").focus()

    def fetch_subreddits(self):
        self.logger.info("Fetching subscribed subreddits")
        try:
            self.subreddits = self.reddit_service.get_subscribed_subreddits()
            self.logger.info(f"Loaded {len(self.subreddits)} subreddits")
            self.query_one("#subreddit_list").update_subreddits(self.subreddits)
        except Exception as e:
            self.logger.error(f"Error fetching subreddits: {str(e)}", exc_info=True)
            self.notify("Error loading subreddits", severity="error")

    def on_subreddit_list_subreddit_selected(self, message: SubredditList.SubredditSelected):
        self.load_subreddit_posts()

    def action_cursor_up(self):
        self.query_one("#subreddit_list").action_cursor_up()

    def action_cursor_down(self):
        self.query_one("#subreddit_list").action_cursor_down()

    def action_select(self):
        self.query_one("#subreddit_list").action_select()

    def load_subreddit_posts(self):
        sublist = self.query_one("#subreddit_list")
        subreddit = sublist.get_selected_subreddit()
        if not subreddit:
            return
        try:
            self.logger.info(f"Loading posts for subreddit: {subreddit.display_name}")
            posts = self.reddit_service.get_subreddit_posts(
                subreddit.display_name,
                sort="hot",
                limit=25
            )
            self.logger.info(f"Loaded {len(posts)} posts for r/{subreddit.display_name}")
            
            self.parent_content.remove_children()
            header = Static(f"r/{subreddit.display_name} - Hot", id="subreddit_header")
            post_list = PostList(posts=posts, id="content")
            
            self.parent_content.mount(header)
            self.parent_content.mount(post_list)
            self.app.active_widget = "content"
            post_list.focus()
            
            from components.sidebar import Sidebar
            self.app.query_one(Sidebar).update_status(f"r/{subreddit.display_name} - Hot")
        except Exception as e:
            self.logger.error(f"Error loading subreddit posts: {str(e)}", exc_info=True)
            self.notify(f"Error loading posts: {str(e)}", severity="error") 