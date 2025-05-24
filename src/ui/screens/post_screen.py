from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich import box

class PostScreen:
    def __init__(self, post, origin=None):
        self.post = post
        self.origin = origin
        self.console = Console()
        self.layout = Layout()

        self.create_layout()

    def create_layout(self):
        self.layout.split_row(
            Layout(name="sidebar", size=20),
            Layout(name="main"),
        )

        self.layout["sidebar"].update(self.create_sidebar())
        self.layout["main"].update(self.create_post_view())

    def create_sidebar(self):
        sidebar_content = Panel(
            Text("Sidebar\n\n1. Home\n2. Login\n3. Exit", style="cyan"),
            title="Navigation",
            box=box.SIMPLE,
        )
        return sidebar_content

    def create_post_view(self):
        origin_text = f"From: {self.origin}\n\n" if self.origin else ""
        post_content = f"""
{origin_text}Title: {self.post['title']}
Subreddit: r/{self.post['subreddit']}
Author: u/{self.post['author']}
Score: {self.post['score']}
Comments: {self.post['num_comments']}

{self.post['content']}
"""
        post_content = Panel(
            Text(post_content, style="white"),
            title="Post Details",
            box=box.SIMPLE,
            expand=True,
            padding=(1, 2)  # Add some padding inside the panel
        )
        return post_content

    def display(self):
        self.console.clear()
        self.console.print(self.layout)