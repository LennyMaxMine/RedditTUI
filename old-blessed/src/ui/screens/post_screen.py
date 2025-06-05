from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich import box
from rich.prompt import Prompt
from rich.style import Style
from services.theme_service import ThemeService

class PostScreen:
    def __init__(self, post, origin=None, reddit_instance=None):
        self.post = post
        self.origin = origin
        self.console = Console()
        self.layout = Layout()
        self.reddit_instance = reddit_instance
        self.theme_service = ThemeService()
        self.report_reasons = [
            "Spam",
            "Vote Manipulation",
            "Personal Information",
            "Sexualizing Minors",
            "Breaking Reddit",
            "Other"
        ]
        self.create_layout()

    def create_layout(self):
        self.layout.split_row(
            Layout(name="sidebar", size=20),
            Layout(name="main"),
        )

        self.layout["sidebar"].update(self.create_sidebar())
        self.layout["main"].update(self.create_post_view())

    def create_sidebar(self):
        sidebar_content = Text("Navigation\n\n", style=self.theme_service.get_style("sidebar"))
        sidebar_content.append("1. Home\n", style=self.theme_service.get_style("sidebar_item"))
        sidebar_content.append("2. Login\n", style=self.theme_service.get_style("sidebar_item"))
        sidebar_content.append("3. Report\n", style=self.theme_service.get_style("sidebar_item"))
        sidebar_content.append("4. Exit\n", style=self.theme_service.get_style("sidebar_item"))
        
        return Panel(sidebar_content, title="Navigation", box=box.SIMPLE, style=self.theme_service.get_style("panel_title"))

    def report_post(self):
        if not self.reddit_instance:
            self.console.print("[red]You must be logged in to report posts[/red]")
            return

        self.console.print("\n[cyan]Select reason for reporting:[/cyan]")
        for idx, reason in enumerate(self.report_reasons, 1):
            self.console.print(f"[yellow]{idx}[/yellow]. [white]{reason}[/white]")

        try:
            choice = int(Prompt.ask("\nEnter number", default="6"))
            if 1 <= choice <= len(self.report_reasons):
                reason = self.report_reasons[choice - 1]
                if reason == "Other":
                    reason = Prompt.ask("[cyan]Please specify reason[/cyan]")
                
                self.reddit_instance.submission(self.post['id']).report(reason)
                self.console.print("[green]Post reported successfully[/green]")
            else:
                self.console.print("[red]Invalid choice[/red]")
        except ValueError:
            self.console.print("[red]Invalid input[/red]")
        except Exception as e:
            self.console.print(f"[red]Error reporting post: {str(e)}[/red]")

    def handle_input(self, key):
        if key == "3":
            self.report_post()
            return True
        return False

    def create_post_view(self):
        origin_text = f"[cyan]From: {self.origin}[/cyan]\n\n" if self.origin else ""
        post_content = Text()
        post_content.append(origin_text)
        post_content.append(f"Title: {self.post['title']}\n", style=self.theme_service.get_style("title"))
        post_content.append(f"Subreddit: r/{self.post['subreddit']}\n", style=self.theme_service.get_style("subreddit"))
        post_content.append(f"Author: u/{self.post['author']}\n", style=self.theme_service.get_style("author"))
        post_content.append(f"Score: {self.post['score']}\n", style=self.theme_service.get_style("score"))
        post_content.append(f"Comments: {self.post['num_comments']}\n\n", style=self.theme_service.get_style("comments"))
        post_content.append(f"{self.post['content']}", style=self.theme_service.get_style("content"))

        return Panel(
            post_content,
            title="Post Details",
            box=box.SIMPLE,
            expand=True,
            padding=(1, 2),
            style=self.theme_service.get_style("panel_title")
        )

    def display(self):
        self.console.clear()
        self.console.print(self.layout)