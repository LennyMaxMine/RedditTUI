from textual.widget import Widget
from textual.widgets import Static, Button, Select
from textual.containers import Vertical, Horizontal, ScrollableContainer
from utils.logger import Logger
from datetime import datetime
from components.post_list import PostList
from rich.text import Text
from rich.panel import Panel
from rich import box
from services.reddit_service import RedditService

class PostViewScreen(Widget):
    def __init__(self, post, parent_content, posts):
        super().__init__()
        self.post = post
        self.parent_content = parent_content
        self.posts = posts
        self.logger = Logger()
        self.comments = []
        self.comment_scroll_offset = 0
        self.comment_lines = []
        self.need_more_comments = False
        self.vote_status = 0
        self.scroll_position = 0
        self.comment_mode = False
        self.comment_text = ""
        self.comment_cursor_pos = 0
        self.comment_sort_mode = "best"
        self.comment_sort_index = 0
        self.comment_sort_options = [
            ("Best", "best"),
            ("Top", "top"),
            ("New", "new"),
            ("Controversial", "controversial"),
            ("Old", "old"),
            ("Q&A", "qa")
        ]
        self.reddit_service = None

    def compose(self):
        self.logger.info("Composing PostViewScreen UI")
        with Vertical():
            yield Static(self._get_title_panel(), id="post_title")
            yield Static(self._get_metadata(), id="post_metadata")
            yield Static(self._get_content(), id="post_content")
            with ScrollableContainer(id="comments_container", classes="expand"):
                yield Static(self._get_comments(), id="comments_section")

    def on_mount(self):
        self.logger.info("PostViewScreen mounted")
        self.reddit_service = self.app.reddit_service
        self.load_comments()

    def load_comments(self):
        self.logger.info("Loading comments")
        try:
            if not self.reddit_service:
                self.logger.error("RedditService not initialized")
                return
            self.logger.info(f"Loading comments for post: {self.post.title}")
            self.comments = self.reddit_service.get_post_comments(self.post, sort=self.comment_sort_mode)
            self.logger.info(f"Loaded {len(self.comments)} comments")
            if not self.comments:
                self.logger.warning("No comments found for post")
            self.query_one("#comments_section").update(self._get_comments())
        except Exception as e:
            self.logger.error(f"Error loading comments: {str(e)}", exc_info=True)
            self.comments = []

    def _get_title_panel(self):
        title = self.post.title
        return Panel(
            Text(title, style="bold white"),
            border_style="blue",
            box=box.ROUNDED
        )

    def _get_metadata(self):
        subreddit = self.post.subreddit.display_name
        author = self.post.author.name if self.post.author else "[deleted]"
        score = self.post.score
        comments = self.post.num_comments
        created = datetime.fromtimestamp(self.post.created_utc)
        age = self._get_age(created)
        
        return Text.assemble(
            Text(f"r/{subreddit} ", style="green"),
            Text(f"• u/{author} ", style="yellow"),
            Text(f"• {score} points ", style="cyan"),
            Text(f"• {comments} comments ", style="magenta"),
            Text(f"• {age}", style="blue")
        )

    def _get_content(self):
        if hasattr(self.post, 'selftext') and self.post.selftext:
            return Panel(
                Text(self.post.selftext),
                border_style="blue",
                box=box.ROUNDED
            )
        elif hasattr(self.post, 'url'):
            link_text = Text(f"{self.post.url}", style="blue underline")
            return Panel(
                Text.assemble("Link: ", link_text),
                border_style="blue",
                box=box.ROUNDED
            )
        return Panel(
            Text("No content available"),
            border_style="blue",
            box=box.ROUNDED
        )

    def _get_comments(self):
        if not self.comments:
            self.logger.debug("No comments to display")
            return Panel(
                Text("No comments yet"),
                border_style="blue",
                box=box.ROUNDED
            )

        try:
            def format_comment(comment, depth=0):
                if not hasattr(comment, 'body') or not comment.body:
                    return None

                try:
                    author = getattr(comment, 'author', '[deleted]')
                    if author is None or author == '[deleted]':
                        author_str = '[deleted]'
                    else:
                        try:
                            author_str = author.name
                        except Exception as e:
                            self.logger.error(f"Error getting author name: {str(e)}", exc_info=True)
                            author_str = '[unknown]'
                    score = getattr(comment, 'score', 0)
                    created = getattr(comment, 'created_utc', None)
                    age = self._get_age(datetime.fromtimestamp(created)) if created else "unknown"
                    
                    # Create indentation based on depth
                    indent = "  " * depth
                    thread_line = "└─ " if depth > 0 else ""
                    
                    # Format comment header with threading visualization
                    header = Text.assemble(
                        Text(f"{indent}{thread_line}", style="blue"),
                        Text(f"u/{author_str} ", style="yellow"),
                        Text(f"• {score} points ", style="cyan"),
                        Text(f"• {age}\n", style="blue")
                    )
                    
                    # Format comment body with proper indentation
                    body_lines = comment.body.split('\n')
                    body_text = Text()
                    for i, line in enumerate(body_lines):
                        body_text.append(f"{indent}  {line}\n", style="white")
                    
                    return Text.assemble(header, body_text)
                except Exception as e:
                    self.logger.error(f"Error formatting comment: {str(e)}", exc_info=True)
                    return None

            def process_comments(comments, depth=0):
                comment_texts = []
                for comment in comments:
                    if hasattr(comment, 'body') and comment.body:
                        comment_text = format_comment(comment, depth)
                        if comment_text:
                            comment_texts.append(comment_text)
                            comment_texts.append(Text("\n"))
                        
                        if hasattr(comment, 'replies') and comment.replies:
                            replies = list(comment.replies)
                            if replies:
                                comment_texts.extend(process_comments(replies, depth + 1))
                return comment_texts

            comment_texts = process_comments(self.comments)

            if not comment_texts:
                return Panel(
                    Text("No comments to display"),
                    border_style="blue",
                    box=box.ROUNDED
                )

            return Panel(
                Text.assemble(*comment_texts),
                title=f"Comments ({len(comment_texts)}) - Sorted by {self.comment_sort_mode.title()}",
                border_style="blue",
                box=box.ROUNDED
            )
        except Exception as e:
            self.logger.error(f"Error creating comments panel: {str(e)}", exc_info=True)
            return Panel(
                Text("Error loading comments"),
                border_style="red",
                box=box.ROUNDED
            )

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

    def on_button_pressed(self, event):
        try:
            if event.button.id == "back_button":
                self.logger.info("Back button pressed")
                self.parent_content.remove_children()
                post_list = PostList(posts=self.posts, id="content")
                self.parent_content.mount(post_list)
                self.app.active_widget = "content"
                post_list.focus()
            elif event.button.id == "upvote_button":
                self.logger.info("Upvote button pressed")
                try:
                    self.post.upvote()
                    self.notify("Post upvoted!", severity="information")
                    self.logger.info(f"Upvoted post: {self.post.title}")
                except Exception as e:
                    self.logger.error(f"Error upvoting post: {str(e)}", exc_info=True)
                    self.notify(f"Error upvoting post: {str(e)}", severity="error")
            elif event.button.id == "downvote_button":
                self.logger.info("Downvote button pressed")
                try:
                    self.post.downvote()
                    self.notify("Post downvoted!", severity="information")
                    self.logger.info(f"Downvoted post: {self.post.title}")
                except Exception as e:
                    self.logger.error(f"Error downvoting post: {str(e)}", exc_info=True)
                    self.notify(f"Error downvoting post: {str(e)}", severity="error")
            elif event.button.id == "copy_link_button":
                import pyperclip
                pyperclip.copy(self.post.url)
                self.notify("Link copied to clipboard!", severity="information")
            elif event.button.id == "open_link_button":
                import webbrowser
                webbrowser.open(self.post.url)
                self.notify("Opening link in browser...", severity="information")
        except Exception as e:
            self.logger.error(f"Error handling button press: {str(e)}", exc_info=True)

    def sort_comments(self, sort_mode):
        self.comment_sort_mode = sort_mode
        self.load_comments() 