from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import TextArea, Button, Static
from textual.screen import ModalScreen
from utils.logger import Logger
from services.reddit_service import RedditService

class CommentScreen(ModalScreen):
    def __init__(self, post):
        super().__init__()
        self.post = post
        self.logger = Logger()

    def compose(self) -> ComposeResult:
        self.logger.info("Composing CommentScreen UI")
        yield Container(
            Vertical(
                Static(f"Comment on: {self.post.title}", classes="title"),
                Static("Write your comment below:", classes="label"),
                TextArea(id="comment_input"),
                Button("Submit", id="submit_button"),
                Button("Cancel", id="cancel_button"),
                id="comment_form"
            ),
            id="comment_container"
        )

    def on_mount(self):
        self.logger.info("CommentScreen mounted")
        self.query_one("#comment_input").focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.logger.info(f"Button pressed: {event.button.id}")
        if event.button.id == "submit_button":
            comment_text = self.query_one("#comment_input").text
            if not comment_text.strip():
                self.notify("Please enter a comment", severity="error")
                return

            self.logger.info("Submitting comment")
            reddit_service = self.app.reddit_service
            if reddit_service.submit_comment(self.post, comment_text):
                self.logger.info("Comment submitted successfully")
                self.notify("Comment submitted successfully!", severity="success")
                self.dismiss(True)
            else:
                self.logger.error("Failed to submit comment")
                self.notify("Failed to submit comment", severity="error")
        elif event.button.id == "cancel_button":
            self.dismiss(False) 