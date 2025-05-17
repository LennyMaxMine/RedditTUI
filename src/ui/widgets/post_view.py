from textual.app import App
from textual.scroll_view import ScrollView
from textual.widgets import Static, Header, Footer
from textual.containers import Container, Horizontal
from textual.reactive import Reactive
from textual import events
from blessed import Terminal
import textwrap

class PostView:
    def __init__(self, terminal):
        self.terminal = terminal
        self.current_post = None
        self.comments = []
        self.content_width = max(35, self.terminal.width - 24)  # Use more space

    def display(self):
        if not self.current_post:
            return ""
        width = self.content_width
        output = []
        output.append("=" * width)
        output.append(f"{self.current_post.title}".center(width))
        output.append("=" * width)
        output.append(f"Subreddit: r/{self.current_post.subreddit.display_name}    Author: u/{self.current_post.author}    Score: {self.current_post.score}    Comments: {self.current_post.num_comments}")
        if hasattr(self.current_post, 'created_utc'):
            import datetime
            dt = datetime.datetime.utcfromtimestamp(self.current_post.created_utc)
            output.append(f"Posted: {dt.strftime('%Y-%m-%d %H:%M UTC')}")
        if hasattr(self.current_post, 'url'):
            output.append(f"URL: {self.current_post.url}")
        output.append("-" * width)
        if hasattr(self.current_post, 'selftext') and self.current_post.selftext:
            output.append("Content:")
            content = textwrap.fill(self.current_post.selftext, width=width-2)
            output.append(content)
        output.append("=" * width)
        if self.comments:
            output.append("Top Comments:")
            for idx, comment in enumerate(self.comments[:5], 1):
                if hasattr(comment, 'body'):
                    author = getattr(comment, 'author', '[deleted]')
                    score = getattr(comment, 'score', 0)
                    output.append(f"  {idx}. u/{author} | {score} points:")
                    comment_body = textwrap.fill(comment.body, width=width-6)
                    for line in comment_body.splitlines():
                        output.append(f"      {line}")
                    output.append("  -" + "-" * (width-4))
        return "\n".join(output)

    def display_post(self, post, comments=None):
        self.current_post = post
        self.comments = comments or []

class PostList:
    def __init__(self, terminal):
        self.terminal = terminal
        self.posts = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.visible_posts = 10

    def display(self):
        if not self.posts:
            return "No posts available"
        
        width = self.terminal.width
        output = []
        output.append("=" * width)
        output.append("Reddit Posts".center(width))
        output.append("=" * width)
        
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.visible_posts, len(self.posts))
        
        for idx, post in enumerate(self.posts[start_idx:end_idx], start=start_idx + 1):
            if idx - 1 == self.selected_index:
                prefix = "> "
            else:
                prefix = "  "
            
            post_line = f"{prefix}{idx}. {post.title}"
            if len(post_line) > width - 4:
                post_line = post_line[:width-7] + "..."
            output.append(post_line)
        
        return "\n".join(output)

    def get_selected_post(self):
        if 0 <= self.selected_index < len(self.posts):
            return self.posts[self.selected_index]
        return None

    def update_posts(self, new_posts):
        self.posts = new_posts
        self.selected_index = 0
        self.scroll_offset = 0

class Sidebar:
    def __init__(self, terminal):
        self.terminal = terminal
        self.options = [
            "Home",
            "View Post",
            "Login",
            "Help",
            "Exit"
        ]
        self.selected_index = 0

    def display(self):
        width = 20
        output = []
        output.append("=" * width)
        output.append("Navigation".center(width))
        output.append("=" * width)
        
        for idx, option in enumerate(self.options):
            if idx == self.selected_index:
                prefix = "> "
            else:
                prefix = "  "
            output.append(f"{prefix}{option}")
        
        return "\n".join(output)

    def navigate(self, direction):
        if direction == "down":
            self.selected_index = (self.selected_index + 1) % len(self.options)
        elif direction == "up":
            self.selected_index = (self.selected_index - 1) % len(self.options)

    def get_selected_option(self):
        return self.options[self.selected_index]

class MainApp(App):
    def compose(self):
        sidebar = Sidebar()
        post_list = PostList(["Post 1", "Post 2", "Post 3"])
        post_view = PostView()
        
        return Container(
            Horizontal(sidebar, post_list, post_view)
        )

if __name__ == "__main__":
    MainApp.run()