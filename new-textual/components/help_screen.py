from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Container, Vertical, ScrollableContainer
from utils.logger import Logger
from pathlib import Path
from rich.text import Text
from rich.panel import Panel
from rich.console import Console
from rich.markdown import Markdown

class HelpScreen(Screen):
    def __init__(self):
        super().__init__()
        self.logger = Logger()

    def compose(self):
        yield Container(
            Static("RedditTUI Help", classes="title"),
            ScrollableContainer(
                Static(self._get_help_content()),
                classes="help-content"
            ),
            Button("Close", id="close_button"),
            id="help_container"
        )

    def _get_help_content(self):
        try:
            readme_path = Path("README.md")
            if readme_path.exists():
                with open(readme_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.logger.info("Loaded README.md for help screen")
                    return self._format_markdown(content)
            else:
                self.logger.warning("README.md not found, using fallback help content")
                return self._get_fallback_content()
        except Exception as e:
            self.logger.error(f"Error reading README.md: {str(e)}", exc_info=True)
            return self._get_fallback_content()

    def _format_markdown(self, markdown_content):
        try:
            console = Console(record=True, width=80)
            md = Markdown(markdown_content)
            console.print(md)
            return console.export_text()
        except Exception as e:
            self.logger.error(f"Error formatting markdown: {str(e)}", exc_info=True)
            return markdown_content

    def _get_fallback_content(self):
        fallback_text = """An error occured while loading the help screen.
        """
        return self._format_markdown(fallback_text)

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "close_button":
            self.dismiss()

    def on_mount(self):
        self.logger.info("Help screen mounted") 