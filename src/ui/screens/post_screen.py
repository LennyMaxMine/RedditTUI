from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich import box

class PostScreen:
    def __init__(self, post):
        self.post = post
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
        post_content = Panel(
            Text(f"Title: {self.post['title']}\n\n"
                 f"Author: {self.post['author']}\n"
                 f"Score: {self.post['score']}\n"
                 f"Comments: {self.post['num_comments']}\n\n"
                 f"{self.post['content']}", style="white"),
            title="Post Details",
            box=box.SIMPLE,
        )
        return post_content

    def display(self):
        self.console.clear()
        self.console.print(self.layout)