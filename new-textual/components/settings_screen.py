from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Input, Button, Static, Select, Switch
from textual.screen import ModalScreen
from utils.logger import Logger
from services.reddit_service import RedditService

class SettingsScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        Logger().info("Composing SettingsScreen UI")
        yield Container(
            Vertical(
                Static("Settings", classes="title"),
                Static("Posts per page:", classes="setting_label"),
                Input(value="25", id="posts_per_page"),
                Static("Comment depth:", classes="setting_label"),
                Input(value="3", id="comment_depth"),
                Static("Auto load comments:", classes="setting_label"),
                Switch(id="auto_load_comments"),
                Static("Show NSFW content:", classes="setting_label"),
                Switch(id="show_nsfw"),
                Static("Comment sort:", classes="setting_label"),
                Select(
                    [
                        ("best", "Best"),
                        ("top", "Top"),
                        ("new", "New"),
                        ("controversial", "Controversial")
                    ],
                    id="comment_sort",
                    prompt="Sort comments by"
                ),
                Horizontal(
                    Button("Save", id="save_button"),
                    Button("Cancel", id="cancel_button"),
                    id="button_container"
                ),
                id="settings_form"
            ),
            id="settings_container"
        )

    def on_mount(self):
        Logger().info("SettingsScreen mounted")
        self.load_settings()

    def load_settings(self):
        Logger().info("Loading settings")
        try:
            settings = self.app.settings
            if settings:
                self.query_one("#posts_per_page").value = str(settings.get("posts_per_page", "25"))
                self.query_one("#comment_depth").value = str(settings.get("comment_depth", "3"))
                self.query_one("#auto_load_comments").value = settings.get("auto_load_comments", True)
                self.query_one("#show_nsfw").value = settings.get("show_nsfw", False)
                self.query_one("#comment_sort").value = settings.get("sort_comments_by", "best")
        except Exception as e:
            Logger().error(f"Error loading settings: {str(e)}", exc_info=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        Logger().info(f"Button pressed: {event.button.id}")
        if event.button.id == "save_button":
            self.save_settings()
            self.dismiss(True)
        elif event.button.id == "cancel_button":
            self.dismiss(False)

    def save_settings(self):
        Logger().info("Saving settings")
        try:
            settings = {
                "posts_per_page": int(self.query_one("#posts_per_page").value),
                "comment_depth": int(self.query_one("#comment_depth").value),
                "auto_load_comments": self.query_one("#auto_load_comments").value,
                "show_nsfw": self.query_one("#show_nsfw").value,
                "sort_comments_by": self.query_one("#comment_sort").value
            }
            self.app.settings = settings
            self.app.save_settings()
            self.notify("Settings saved successfully!", severity="success")
        except Exception as e:
            Logger().error(f"Error saving settings: {str(e)}", exc_info=True)
            self.notify("Error saving settings", severity="error") 