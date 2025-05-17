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
        
        # Title section
        output.append(self.terminal.blue("=" * width))
        output.append(self.terminal.bold_white(f"{self.current_post.title}".center(width)))
        output.append(self.terminal.blue("=" * width))
        
        # Metadata section
        metadata = []
        metadata.append(self.terminal.cyan(f"Subreddit: r/{self.current_post.subreddit.display_name}"))
        metadata.append(self.terminal.yellow(f"Author: u/{self.current_post.author}"))
        metadata.append(self.terminal.green(f"Score: {self.current_post.score}"))
        metadata.append(self.terminal.magenta(f"Comments: {self.current_post.num_comments}"))
        
        if hasattr(self.current_post, 'created_utc'):
            import datetime
            dt = datetime.datetime.utcfromtimestamp(self.current_post.created_utc)
            metadata.append(self.terminal.blue(f"Posted: {dt.strftime('%Y-%m-%d %H:%M UTC')}"))
        
        if hasattr(self.current_post, 'url'):
            metadata.append(self.terminal.cyan(f"URL: {self.current_post.url}"))
            
        if hasattr(self.current_post, 'is_self'):
            metadata.append(self.terminal.yellow(f"Type: {'Self Post' if self.current_post.is_self else 'Link Post'}"))
            
        if hasattr(self.current_post, 'upvote_ratio'):
            metadata.append(self.terminal.green(f"Upvote Ratio: {self.current_post.upvote_ratio:.1%}"))
            
        if hasattr(self.current_post, 'over_18'):
            if self.current_post.over_18:
                metadata.append(self.terminal.red("NSFW: Yes"))
            else:
                metadata.append(self.terminal.green("NSFW: No"))
            
        if hasattr(self.current_post, 'spoiler'):
            if self.current_post.spoiler:
                metadata.append(self.terminal.yellow("Spoiler: Yes"))
            else:
                metadata.append(self.terminal.green("Spoiler: No"))
            
        if hasattr(self.current_post, 'locked'):
            if self.current_post.locked:
                metadata.append(self.terminal.red("Locked: Yes"))
            else:
                metadata.append(self.terminal.green("Locked: No"))
            
        if hasattr(self.current_post, 'stickied'):
            if self.current_post.stickied:
                metadata.append(self.terminal.yellow("Stickied: Yes"))
            else:
                metadata.append(self.terminal.green("Stickied: No"))
        
        # Format metadata in two columns
        metadata_lines = []
        for i in range(0, len(metadata), 2):
            line = metadata[i]
            if i + 1 < len(metadata):
                line = line.ljust(width // 2) + metadata[i + 1]
            metadata_lines.append(line)
        
        output.extend(metadata_lines)
        output.append(self.terminal.blue("-" * width))
        
        # Content section
        if hasattr(self.current_post, 'selftext') and self.current_post.selftext:
            output.append(self.terminal.bold_white("Content:"))
            content = textwrap.fill(self.current_post.selftext, width=width-2)
            output.append(self.terminal.white(content))
        elif hasattr(self.current_post, 'url'):
            output.append(self.terminal.bold_white("Link Post:"))
            output.append(self.terminal.cyan(f"URL: {self.current_post.url}"))
            if hasattr(self.current_post, 'preview') and self.current_post.preview:
                output.append(self.terminal.yellow("Preview available (not shown)"))
        
        # Comments section
        if self.comments:
            output.append(self.terminal.blue("=" * width))
            output.append(self.terminal.bold_white("Top Comments:"))
            for idx, comment in enumerate(self.comments[:5], 1):
                if hasattr(comment, 'body'):
                    author = getattr(comment, 'author', '[deleted]')
                    score = getattr(comment, 'score', 0)
                    created = getattr(comment, 'created_utc', None)
                    created_str = ""
                    if created:
                        dt = datetime.datetime.utcfromtimestamp(created)
                        created_str = f" | {dt.strftime('%Y-%m-%d %H:%M UTC')}"
                    
                    # Comment header with metadata
                    comment_header = f"  {idx}. {self.terminal.yellow(f'u/{author}')} | {self.terminal.green(f'{score} points')}{self.terminal.blue(created_str)}:"
                    output.append(comment_header)
                    
                    # Comment body
                    comment_body = textwrap.fill(comment.body, width=width-6)
                    for line in comment_body.splitlines():
                        output.append(f"      {self.terminal.white(line)}")
                    output.append("  " + self.terminal.blue("-" * (width-4)))
        
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
        
        width = self.terminal.width - 22  # Account for sidebar
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
            
            # Format post number and title
            post_num = f"{idx}."
            title = post.title
            if len(title) > width - 40:  # Leave space for metadata
                title = title[:width-43] + "..."
            
            # Get post metadata
            subreddit = f"r/{post.subreddit.display_name}"
            author = f"u/{post.author}"
            score = f"↑{post.score}"
            comments = f"💬{post.num_comments}"
            
            # Format the post line with metadata
            post_line = f"{prefix}{post_num} {title}"
            metadata = f" | {subreddit} | {author} | {score} | {comments}"
            
            # Add NSFW tag if applicable
            if hasattr(post, 'over_18') and post.over_18:
                metadata += " | NSFW"
            
            # Add stickied tag if applicable
            if hasattr(post, 'stickied') and post.stickied:
                metadata += " | 📌"
            
            # Combine title and metadata, ensuring it fits in the width
            full_line = post_line + metadata
            if len(full_line) > width - 2:
                # Truncate the title to make room for metadata
                available_space = width - 2 - len(metadata)
                post_line = f"{prefix}{post_num} {title[:available_space-3]}..."
                full_line = post_line + metadata
            
            output.append(full_line)
            
            # Add a separator line between posts
            output.append("  " + "-" * (width - 2))
        
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