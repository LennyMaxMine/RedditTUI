from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.tree import Tree

class HomeScreen:
    def __init__(self, reddit_service):
        self.reddit_service = reddit_service
        self.console = Console()
        self.layout = Layout()

        self.setup_layout()

    def setup_layout(self):
        self.layout.split_row(
            Layout(name="sidebar", size=20),
            Layout(name="main"),
            Layout(name="details", size=40)
        )

    def display_sidebar(self):
        sidebar_content = Tree("Reddit CLI", guide_style="bold bright_blue")
        sidebar_content.add("Home")
        sidebar_content.add("My Posts")
        sidebar_content.add("Saved Posts")
        sidebar_content.add("Logout")
        self.layout["sidebar"].update(Panel(sidebar_content, title="Navigation"))

    def display_posts(self):
        posts = self.reddit_service.fetch_posts()
        post_list = "\n".join([f"{idx + 1}. {post.title}" for idx, post in enumerate(posts)])
        self.layout["main"].update(Panel(post_list, title="Posts"))

    def display(self):
        self.display_sidebar()
        self.display_posts()
        self.console.print(self.layout)

    def refresh(self):
        self.display_posts()