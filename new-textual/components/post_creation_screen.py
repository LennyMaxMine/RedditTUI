from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Input, Button, Static, Select, TextArea
from textual.screen import ModalScreen
from utils.logger import Logger
from services.reddit_service import RedditService

class PostCreationScreen(ModalScreen):
    def __init__(self, subreddit=None):
        super().__init__()
        self.subreddit = subreddit
        self.logger = Logger()
        self.post_type = "text"
        self.post_types = [
            ("Text Post", "text"),
            ("Link Post", "link"),
            ("Image Post", "image")
        ]

    def compose(self) -> ComposeResult:
        self.logger.info("Composing PostCreationScreen UI")
        yield Container(
            Vertical(
                Static("Create New Post", classes="title"),
                Static("Post Type:", classes="setting_label"),
                Select(self.post_types, id="post_type", prompt="Select post type"),
                Static("Subreddit:", classes="setting_label"),
                Input(placeholder="Enter subreddit name", id="subreddit_input", value=self.subreddit or ""),
                Static("Title:", classes="setting_label"),
                Input(placeholder="Enter post title", id="title_input"),
                Static("Content:", classes="setting_label"),
                TextArea(id="content_input", classes="post_content"),
                Static("URL (for link/image posts):", classes="setting_label"),
                Input(placeholder="Enter URL", id="url_input"),
                Horizontal(
                    Button("Submit", id="submit_button"),
                    Button("Cancel", id="cancel_button"),
                    id="button_container"
                ),
                id="post_form"
            ),
            id="post_container"
        )

    def on_mount(self):
        self.logger.info("PostCreationScreen mounted")
        self.query_one("#title_input").focus()

    def on_select_changed(self, event: Select.Changed) -> None:
        self.logger.info(f"Post type changed to: {event.value}")
        self.post_type = event.value
        url_input = self.query_one("#url_input")
        content_input = self.query_one("#content_input")
        
        if event.value == "text":
            url_input.display = False
            content_input.display = True
        else:
            url_input.display = True
            content_input.display = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.logger.info(f"Button pressed: {event.button.id}")
        if event.button.id == "submit_button":
            self.submit_post()
        elif event.button.id == "cancel_button":
            self.dismiss()

    def submit_post(self):
        try:
            subreddit = self.query_one("#subreddit_input").value
            title = self.query_one("#title_input").value
            content = self.query_one("#content_input").text
            url = self.query_one("#url_input").value

            if not subreddit or not title:
                self.notify("Subreddit and title are required", severity="error")
                return

            if self.post_type != "text" and not url:
                self.notify("URL is required for link/image posts", severity="error")
                return

            if self.post_type == "text" and not content:
                self.notify("Content is required for text posts", severity="error")
                return

            self.logger.info(f"Submitting post to r/{subreddit}")
            reddit_service = self.app.reddit_service
            
            if self.post_type == "text":
                success = reddit_service.submit_text_post(subreddit, title, content)
            else:
                success = reddit_service.submit_link_post(subreddit, title, url)

            if success:
                self.logger.info("Post submitted successfully")
                self.notify("Post submitted successfully!", severity="success")
                self.dismiss(True)
            else:
                self.logger.error("Failed to submit post")
                self.notify("Failed to submit post", severity="error")
        except Exception as e:
            self.logger.error(f"Error submitting post: {str(e)}", exc_info=True)
            self.notify(f"Error submitting post: {str(e)}", severity="error") 