from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.tree import Tree
from services.theme_service import ThemeService

class HomeScreen:
    def __init__(self, reddit_service):
        self.reddit_service = reddit_service
        self.console = Console()
        self.layout = Layout()
        self.theme_service = ThemeService()
        self.setup_layout()

    def setup_layout(self):
        self.layout.split_row(
            Layout(name="sidebar", size=20),
            Layout(name="main"),
            Layout(name="details", size=40)
        )

    def display_sidebar(self):
        sidebar_content = Tree("Reddit CLI", guide_style=self.theme_service.get_style("sidebar"))
        sidebar_content.add("Home", style=self.theme_service.get_style("sidebar_item"))
        sidebar_content.add("My Posts", style=self.theme_service.get_style("sidebar_item"))
        sidebar_content.add("Saved Posts", style=self.theme_service.get_style("sidebar_item"))
        sidebar_content.add("Logout", style=self.theme_service.get_style("sidebar_item"))
        self.layout["sidebar"].update(Panel(sidebar_content, title="Navigation", style=self.theme_service.get_style("panel_title")))

    def display_posts(self):
        posts = self.reddit_service.fetch_posts()
        post_list = Text()
        for idx, post in enumerate(posts):
            post_list.append(f"{idx + 1}. ", style=self.theme_service.get_style("highlight"))
            post_list.append(f"{post.title}\n", style=self.theme_service.get_style("content"))
        self.layout["main"].update(Panel(post_list, title="Posts", style=self.theme_service.get_style("panel_title")))

    def display(self):
        self.display_sidebar()
        self.display_posts()
        self.console.print(self.layout)

    def refresh(self):
        self.display_posts()