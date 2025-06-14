from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Input, Button, Static, Select, TextArea, Switch
from textual.widget import Widget
from utils.logger import Logger
from services.reddit_service import RedditService
import os

class PostCreationScreen(Widget):
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
        self.flairs = []
        self.is_nsfw = False
        self.is_spoiler = False
        self.selected_flair = None
        self.image_path = None

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
                Static("Image Path (for image posts):", classes="setting_label"),
                Input(placeholder="Enter path to image file", id="image_path_input"),
                Static("Post Flair:", classes="setting_label"),
                Select([], id="flair_select", prompt="Select flair"),
                Horizontal(
                    Static("NSFW:", classes="switch_label"),
                    Switch(id="nsfw_switch"),
                    Static("Spoiler:", classes="switch_label"),
                    Switch(id="spoiler_switch"),
                    id="tag_container"
                ),
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
        event = type('Event', (), {'value': self.post_type})()
        self.on_select_changed(event)

    def on_select_changed(self, event: Select.Changed) -> None:
        self.logger.info(f"Post type changed to: {event.value}")
        self.post_type = event.value
        url_input = self.query_one("#url_input")
        content_input = self.query_one("#content_input")
        image_path_input = self.query_one("#image_path_input")
        flair_select = self.query_one("#flair_select")
        tag_container = self.query_one("#tag_container")
        
        if event.value == "text":
            url_input.display = False
            image_path_input.display = False
            content_input.display = True
            flair_select.display = True
            tag_container.display = True
        elif event.value == "link":
            url_input.display = True
            image_path_input.display = False
            content_input.display = False
            flair_select.display = True
            tag_container.display = True
        else:  # image
            url_input.display = False
            image_path_input.display = True
            content_input.display = False
            flair_select.display = True
            tag_container.display = True

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "subreddit_input":
            self.validate_subreddit(event.input.value)

    def validate_subreddit(self, subreddit: str) -> None:
        if not subreddit:
            return
        try:
            reddit_service = self.app.reddit_service
            subreddit_instance = reddit_service.reddit.subreddit(subreddit)
            self.flairs = list(subreddit_instance.flair.link_templates)
            flair_select = self.query_one("#flair_select")
            flair_select.options = [(flair["text"], flair["id"]) for flair in self.flairs]
            flair_select.display = True
            self.query_one("#tag_container").display = True
        except Exception as e:
            self.logger.error(f"Error validating subreddit: {str(e)}", exc_info=True)
            self.notify(f"Invalid subreddit: {str(e)}", severity="error")

    def on_switch_changed(self, event: Switch.Changed) -> None:
        if event.switch.id == "nsfw_switch":
            self.is_nsfw = event.switch.value
        elif event.switch.id == "spoiler_switch":
            self.is_spoiler = event.switch.value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.logger.info(f"Button pressed: {event.button.id}")
        if event.button.id == "submit_button":
            self.submit_post()
        elif event.button.id == "cancel_button":
            self.restore_post_list()

    def restore_post_list(self):
        content = self.app.query_one("#content")
        from components.post_list import PostList
        posts = self.app.current_posts if hasattr(self.app, "current_posts") else []
        content.remove_children()
        post_list = PostList(posts=posts, id="content")
        content.mount(post_list)
        self.app.active_widget = "content"
        post_list.focus()
        self.app.query_one("Sidebar").update_status("Home Feed")

    def submit_post(self):
        try:
            subreddit = self.query_one("#subreddit_input").value
            title = self.query_one("#title_input").value
            content = self.query_one("#content_input").text
            url = self.query_one("#url_input").value
            image_path = self.query_one("#image_path_input").value
            flair_id = self.query_one("#flair_select").value

            if not subreddit or not title:
                self.notify("Subreddit and title are required", severity="error")
                return

            if self.post_type == "text" and not content:
                self.notify("Content is required for text posts", severity="error")
                return

            if self.post_type == "link" and not url:
                self.notify("URL is required for link posts", severity="error")
                return

            if self.post_type == "image":
                if not image_path:
                    self.notify("Image path is required for image posts", severity="error")
                    return
                if not os.path.exists(image_path):
                    self.notify("Image file does not exist", severity="error")
                    return

            self.logger.info(f"Submitting post to r/{subreddit}")
            reddit_service = self.app.reddit_service
            
            if self.post_type == "text":
                success = reddit_service.submit_text_post(
                    subreddit, 
                    title, 
                    content,
                    flair_id=flair_id,
                    nsfw=self.is_nsfw,
                    spoiler=self.is_spoiler
                )
            elif self.post_type == "link":
                success = reddit_service.submit_link_post(
                    subreddit,
                    title,
                    url,
                    flair_id=flair_id,
                    nsfw=self.is_nsfw,
                    spoiler=self.is_spoiler
                )
            else:  # image
                success = reddit_service.submit_image_post(
                    subreddit,
                    title,
                    image_path,
                    flair_id=flair_id,
                    nsfw=self.is_nsfw,
                    spoiler=self.is_spoiler
                )

            if success:
                self.logger.info("Post submitted successfully")
                self.notify("Post submitted successfully!", severity="success")
                self.restore_post_list()
            else:
                self.logger.error("Failed to submit post")
                self.notify("Failed to submit post", severity="error")
        except Exception as e:
            self.logger.error(f"Error submitting post: {str(e)}", exc_info=True)
            self.notify(f"Error submitting post: {str(e)}", severity="error") 