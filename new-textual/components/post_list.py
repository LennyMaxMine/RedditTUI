from textual.widgets import Static
from textual.containers import Vertical
from textual.widget import Widget
from rich.text import Text
from datetime import datetime

class PostList(Widget):
    def __init__(self, posts=None, id=None):
        super().__init__(id=id)
        self.posts = posts or []
        self.selected_index = 0

    def compose(self):
        yield Vertical()

    def on_mount(self):
        self.update_posts(self.posts)

    def update_posts(self, posts):
        self.posts = posts
        self.selected_index = 0
        self.refresh()

    def render(self):
        if not self.posts:
            return Text("No posts to display")

        content = []
        for i, post in enumerate(self.posts):
            prefix = "▶ " if i == self.selected_index else "  "
            title = post.title
            subreddit = post.subreddit.display_name
            author = post.author.name if post.author else "[deleted]"
            score = post.score
            comments = post.num_comments
            created = datetime.fromtimestamp(post.created_utc)
            age = self._get_age(created)

            line = Text()
            line.append(prefix, "bold blue" if i == self.selected_index else "white")
            line.append(f"{title} ", "bold white")
            line.append(f"r/{subreddit} ", "green")
            line.append(f"by {author} ", "yellow")
            line.append(f"• {score} points ", "cyan")
            line.append(f"• {comments} comments ", "magenta")
            line.append(f"• {age}", "blue")
            content.append(line)

        return Text.assemble(*content, "\n")#a

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

    def action_cursor_up(self):
        if self.selected_index > 0:
            self.selected_index -= 1
            self.refresh()

    def action_cursor_down(self):
        if self.selected_index < len(self.posts) - 1:
            self.selected_index += 1
            self.refresh()

    def get_selected_post(self):
        if 0 <= self.selected_index < len(self.posts):
            return self.posts[self.selected_index]
        return None 