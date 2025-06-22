from textual.widgets import Static
from textual.containers import Vertical, ScrollableContainer
from textual.widget import Widget
from textual.reactive import reactive
from textual.binding import Binding
from rich.text import Text
from datetime import datetime
from utils.logger import Logger
from textual.geometry import Region

class PostList(Widget):
    BINDINGS = [
        Binding("up", "cursor_up", "Up", show=True),
        Binding("down", "cursor_down", "Down", show=True),
    ]

    selected_index = reactive(0)

    def __init__(self, posts=None, id=None):
        Logger().info("Initializing PostList widget")
        super().__init__(id=id)
        self.posts = posts or []
        self.visible_posts = 10
        self.can_focus = True
        self._post_list_static = None
        self._post_container = None

    def compose(self):
        Logger().info("Composing PostList UI")
        with ScrollableContainer(id="post_container") as container:
            self._post_container = container
            with Vertical(id="post_content"):
                yield Static(id="post_list")

    def on_mount(self):
        Logger().info("PostList mounted")
        self._post_list_static = self.query_one("#post_list", Static)
        self._post_container = self.query_one("#post_container", ScrollableContainer)
        self.update_posts(self.posts)

    def on_focus(self, event):
        self.refresh()

    def on_blur(self, event):
        self.refresh()

    def update_posts(self, posts):
        Logger().info(f"Updating posts in PostList: {len(posts)} posts")
        self.posts = posts
        self.selected_index = 0
        self.refresh()

    def render(self):
        if self._post_list_static:
            if not self.posts:
                self._post_list_static.update(Text("No posts to display"))
                return Text("")

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

                # Title line
                title_line = Text()
                title_line.append(prefix, "bold blue" if i == self.selected_index else "white")
                title_line.append(f"{title}\n", "bold white" if i == self.selected_index else "white")

                # Metadata line
                meta_line = Text()
                meta_line.append("    ")  # Indent to align with title
                meta_line.append(f"r/{subreddit} ", "green")
                meta_line.append(f"• u/{author} ", "yellow")
                meta_line.append(f"• {score} points ", "cyan")
                meta_line.append(f"• {comments} comments ", "magenta")
                meta_line.append(f"• {age}\n", "blue")

                # Add a blank line between posts
                content.extend([title_line, meta_line, Text("\n")])

            # Update the content of the Static widget
            self._post_list_static.update(Text.assemble(*content))

        # Return an empty Text as this widget is a container
        return Text("")

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
        Logger().debug("Cursor up in PostList")
        if self.selected_index > 0:
            self.selected_index -= 1
            Logger().debug(f"Scrolling to post index {self.selected_index}")
            self.refresh()
            self._scroll_to_selected()

    def action_cursor_down(self):
        Logger().debug("Cursor down in PostList")
        if self.selected_index < len(self.posts) - 1:
            self.selected_index += 1
            Logger().debug(f"Scrolling to post index {self.selected_index}")
            self.refresh()
            self._scroll_to_selected()

    def _scroll_to_selected(self):
        if not self._post_container or not self.posts:
            return
        
        try:
            # Calculate the position of the selected post
            post_height = 4  # Each post takes roughly 4 lines
            target_y = self.selected_index * post_height
            
            # Get current scroll position and container height
            current_scroll = self._post_container.scroll_offset.y
            container_height = self._post_container.size.height
            
            # Calculate if the selected post is outside the visible area
            if target_y < current_scroll:
                # Post is above visible area, scroll up
                self._post_container.scroll_to(target_y)
            elif target_y + post_height > current_scroll + container_height:
                # Post is below visible area, scroll down
                self._post_container.scroll_to(target_y - container_height + post_height)
        except Exception as e:
            Logger().error(f"Error scrolling to selected post: {str(e)}", exc_info=True)

    def on_scroll(self, event):
        Logger().info(f"Scroll event received: {event}")

    def get_selected_post(self):
        if 0 <= self.selected_index < len(self.posts):
            Logger().info(f"Selected post at index {self.selected_index}")
            return self.posts[self.selected_index]
        return None