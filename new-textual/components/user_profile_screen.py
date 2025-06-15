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
                yield Button("Message", id="message_button")
                yield Button("Follow", id="follow_button")
                yield Button("Block", id="block_button")
                yield Button("Back", id="back_button")
            with ScrollableContainer(id="content_container"):
                yield Static(id="user_content")

    def on_mount(self):
        self.logger.info("UserProfileScreen mounted")
        self.reddit_service = self.app.reddit_service
        self.load_user_data()
        self.update_social_buttons()

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

    def update_social_buttons(self):
        try:
            if not self.reddit_service or not self.reddit_service.user:
                return

            follow_button = self.query_one("#follow_button")
            block_button = self.query_one("#block_button")
            message_button = self.query_one("#message_button")

            if self.username == self.reddit_service.user:
                follow_button.disabled = True
                block_button.disabled = True
                message_button.disabled = True
            else:
                follow_button.disabled = False
                block_button.disabled = False
                message_button.disabled = False

                followed_users = self.reddit_service.get_followed_users()
                blocked_users = self.reddit_service.get_blocked_users()

                if self.username in [user.name for user in followed_users]:
                    follow_button.label = "Unfollow"
                else:
                    follow_button.label = "Follow"

                if self.username in [user.name for user in blocked_users]:
                    block_button.label = "Unblock"
                else:
                    block_button.label = "Block"

        except Exception as e:
            self.logger.error(f"Error updating social buttons: {str(e)}", exc_info=True)

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "posts_button":
            self.current_view = "posts"
            self.show_posts()
        elif event.button.id == "comments_button":
            self.current_view = "comments"
            self.show_comments()
        elif event.button.id == "message_button":
            self.action_message_user()
        elif event.button.id == "follow_button":
            self.action_follow_user()
        elif event.button.id == "block_button":
            self.action_block_user()
        elif event.button.id == "back_button":
            self.parent_content.remove_children()
            self.parent_content.mount(PostList(posts=self.posts, id="content"))
            self.app.active_widget = "content"
            self.query_one(PostList).focus()

    def action_message_user(self):
        try:
            if not self.reddit_service or not self.reddit_service.user:
                self.notify("Please login first", severity="warning")
                return

            if self.username == self.reddit_service.user:
                self.notify("Cannot message yourself", severity="warning")
                return

            from components.messages_screen import MessagesScreen
            content = self.query_one("#content")
            content.remove_children()
            messages_screen = MessagesScreen(content, self.posts, self.reddit_service)
            content.mount(messages_screen)
            self.app.active_widget = "content"
            messages_screen.focus()
            messages_screen.recipient = self.username
            messages_screen.update_messages_display()

        except Exception as e:
            self.logger.error(f"Error opening message screen: {str(e)}", exc_info=True)
            self.notify(f"Error: {str(e)}", severity="error")

    def action_follow_user(self):
        try:
            if not self.reddit_service or not self.reddit_service.user:
                self.notify("Please login first", severity="warning")
                return

            if self.username == self.reddit_service.user:
                self.notify("Cannot follow yourself", severity="warning")
                return

            followed_users = self.reddit_service.get_followed_users()
            is_following = self.username in [user.name for user in followed_users]

            if is_following:
                if self.reddit_service.unfollow_user(self.username):
                    self.notify(f"Unfollowed u/{self.username}", severity="success")
                else:
                    self.notify("Failed to unfollow user", severity="error")
            else:
                if self.reddit_service.follow_user(self.username):
                    self.notify(f"Following u/{self.username}", severity="success")
                else:
                    self.notify("Failed to follow user", severity="error")

            self.update_social_buttons()

        except Exception as e:
            self.logger.error(f"Error following/unfollowing user: {str(e)}", exc_info=True)
            self.notify(f"Error: {str(e)}", severity="error")

    def action_block_user(self):
        try:
            if not self.reddit_service or not self.reddit_service.user:
                self.notify("Please login first", severity="warning")
                return

            if self.username == self.reddit_service.user:
                self.notify("Cannot block yourself", severity="warning")
                return

            blocked_users = self.reddit_service.get_blocked_users()
            is_blocked = self.username in [user.name for user in blocked_users]

            if is_blocked:
                if self.reddit_service.unblock_user(self.username):
                    self.notify(f"Unblocked u/{self.username}", severity="success")
                else:
                    self.notify("Failed to unblock user", severity="error")
            else:
                if self.reddit_service.block_user(self.username):
                    self.notify(f"Blocked u/{self.username}", severity="success")
                else:
                    self.notify("Failed to block user", severity="error")

            self.update_social_buttons()

        except Exception as e:
            self.logger.error(f"Error blocking/unblocking user: {str(e)}", exc_info=True)
            self.notify(f"Error: {str(e)}", severity="error")