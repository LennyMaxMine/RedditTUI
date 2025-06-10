from textual.widget import Widget
from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal, ScrollableContainer
from utils.logger import Logger
from datetime import datetime
from rich.text import Text
from rich.panel import Panel
from rich import box
from services.reddit_service import RedditService
from components.post_list import PostList

class UserProfileScreen(Widget):
    def __init__(self, username, parent_content, posts):
        super().__init__()
        self.username = username
        self.parent_content = parent_content
        self.posts = posts
        self.logger = Logger()
        self.reddit_service = None
        self.user = None
        self.user_posts = []
        self.user_comments = []
        self.current_view = "posts"  # or "comments"
        self.karma_breakdown = {}

    def compose(self):
        self.logger.info("Composing UserProfileScreen UI")
        with Vertical():
            yield Static(id="user_header")
            yield Static(id="user_stats")
            with Horizontal():
                yield Button("Posts", id="posts_button")
                yield Button("Comments", id="comments_button")
                yield Button("Back", id="back_button")
            with ScrollableContainer(id="content_container"):
                yield Static(id="user_content")

    def on_mount(self):
        self.logger.info("UserProfileScreen mounted")
        self.reddit_service = self.app.reddit_service
        self.load_user_data()

    def load_user_data(self):
        self.logger.info(f"Loading user data for: {self.username}")
        try:
            if not self.reddit_service:
                self.logger.error("RedditService not initialized")
                return

            self.user = self.reddit_service.reddit.redditor(self.username)
            self.user_posts = list(self.user.submissions.new(limit=25))
            self.user_comments = list(self.user.comments.new(limit=25))
            
            # Get karma breakdown
            self.karma_breakdown = {
                "post_karma": self.user.link_karma,
                "comment_karma": self.user.comment_karma,
                "total_karma": self.user.link_karma + self.user.comment_karma
            }

            self.update_header()
            self.update_stats()
            self.show_posts()

        except Exception as e:
            self.logger.error(f"Error loading user data: {str(e)}", exc_info=True)
            self.notify(f"Error loading user data: {str(e)}", severity="error")

    def update_header(self):
        header = Text()
        header.append(f"u/{self.username}\n", style="bold blue")
        header.append(f"Redditor since {datetime.fromtimestamp(self.user.created_utc).strftime('%Y-%m-%d')}\n", style="white")
        self.query_one("#user_header").update(header)

    def update_stats(self):
        stats = Text()
        stats.append("Karma Breakdown:\n", style="bold blue")
        stats.append(f"Post Karma: {self.karma_breakdown['post_karma']}\n", style="green")
        stats.append(f"Comment Karma: {self.karma_breakdown['comment_karma']}\n", style="yellow")
        stats.append(f"Total Karma: {self.karma_breakdown['total_karma']}\n", style="cyan")
        self.query_one("#user_stats").update(stats)

    def show_posts(self):
        self.current_view = "posts"
        content = Text()
        if not self.user_posts:
            content.append("No posts found", style="white")
        else:
            for post in self.user_posts:
                content.append(f"▶ {post.title}\n", style="bold white")
                content.append(f"    r/{post.subreddit.display_name} • {post.score} points • {post.num_comments} comments\n\n", style="white")
        self.query_one("#user_content").update(content)

    def show_comments(self):
        self.current_view = "comments"
        content = Text()
        if not self.user_comments:
            content.append("No comments found", style="white")
        else:
            for comment in self.user_comments:
                content.append(f"▶ {comment.body[:100]}...\n", style="bold white")
                content.append(f"    r/{comment.subreddit.display_name} • {comment.score} points • {self._get_age(datetime.fromtimestamp(comment.created_utc))}\n\n", style="white")
        self.query_one("#user_content").update(content)

    def _get_age(self, created):
        now = datetime.now()
        diff = now - created
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds >= 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds >= 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return f"{diff.seconds}s ago"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back_button":
            self.logger.info("Back button pressed")
            self.parent_content.remove_children()
            post_list = PostList(posts=self.posts, id="content")
            self.parent_content.mount(post_list)
            self.app.active_widget = "content"
            post_list.focus()
        elif event.button.id == "posts_button":
            self.logger.info("Posts button pressed")
            self.show_posts()
        elif event.button.id == "comments_button":
            self.logger.info("Comments button pressed")
            self.show_comments()