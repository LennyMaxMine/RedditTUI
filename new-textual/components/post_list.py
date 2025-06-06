from textual.widgets import Static
from textual.containers import Vertical, ScrollableContainer
from textual.widget import Widget
from textual.reactive import reactive
from rich.text import Text
from datetime import datetime
from utils.logger import Logger
from textual.geometry import Region

class PostList(Widget):
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
        self.update_posts(self.posts)

    def on_focus(self, event):
        Logger().debug("PostList focused")
        self.refresh()

    def on_blur(self, event):
        Logger().debug("PostList unfocused")
        self.refresh()

    def update_posts(self, posts):
        Logger().info(f"Updating posts in PostList: {len(posts)} posts")
        self.posts = posts
        self.selected_index = 0
        self.refresh()

    def render(self):#aaaaa
        Logger().debug("PostList render called, updating static content")
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
            self.refresh()
            # Scroll the container to make the selected post visible
            if self._post_container:
                # Assuming each post block takes approximately 4 lines
                target_y = self.selected_index * 4
                self._post_container.scroll_to_region(Region(0, target_y, self.size.width, 4))

    def action_cursor_down(self):
        Logger().debug("Cursor down in PostList")
        if self.selected_index < len(self.posts) - 1:
            self.selected_index += 1
            self.refresh()
            # Scroll the container to make the selected post visible
            if self._post_container:
                # Assuming each post block takes approximately 4 lines
                target_y = self.selected_index * 4
                self._post_container.scroll_to_region(Region(0, target_y, self.size.width, 4))

    def get_selected_post(self):
        if 0 <= self.selected_index < len(self.posts):
            Logger().info(f"Selected post at index {self.selected_index}")
            return self.posts[self.selected_index]
        return None 