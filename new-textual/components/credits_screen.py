from textual.app import ComposeResult
from textual.containers import Container, Vertical, ScrollableContainer
from textual.widgets import Static, Button, Markdown
from textual.screen import ModalScreen
from utils.logger import Logger
import os
import sys

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

class CreditsScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        Logger().info("Composing CreditsScreen UI")
        yield Container(
            Vertical(
                Static("Credits", classes="title"),
                ScrollableContainer(
                    Markdown("", id="credits_content"),
                    id="credits_container"
                ),
                Button("Close", id="close_button"),
                id="credits_form"
            ),
            id="credits_container"
        )

    def on_mount(self):
        Logger().info("CreditsScreen mounted")
        self.load_credits()
        self.query_one("#close_button").focus()

    def load_credits(self):
        try:
            credits_path = get_resource_path("CREDITS.md")
            if os.path.exists(credits_path):
                with open(credits_path, "r") as f:
                    credits_content = f.read()
                self.query_one("#credits_content", Markdown).update(credits_content)
            else:
                Logger().warning(f"Credits file not found at: {credits_path}")
                self.query_one("#credits_content", Markdown).update("Credits file not found.")
        except Exception as e:
            Logger().error(f"Error loading credits: {str(e)}", exc_info=True)
            self.query_one("#credits_content", Markdown).update("Error loading credits file.")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        Logger().info(f"Button pressed: {event.button.id}")
        if event.button.id == "close_button":
            self.dismiss() 