from textual.widget import Widget
from textual.widgets import Static, Input, Button
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from utils.logger import Logger
from components.post_list import PostList
import json
import os
import re

class ThemeCreationScreen(Widget):
    def __init__(self, parent_content=None, current_posts=None):
        super().__init__()
        self.parent_content = parent_content
        self.current_posts = current_posts
        self.logger = Logger()
        self.theme_name = ""
        self.theme_data = {
            "name": "",
            "primary": "#00ffff",
            "secondary": "#ffff00",
            "accent": "#ff00ff",
            "foreground": "#ffffff",
            "background": "#000000",
            "success": "#00ff00",
            "warning": "#ffff00",
            "error": "#ff0000",
            "surface": "#1a1a1a",
            "panel": "#2a2a2a",
            "dark": True
        }
        self.color_pattern = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')

    def compose(self):
        self.logger.info("Composing ThemeCreationScreen UI")
        with Container(id="theme_container"):
            with ScrollableContainer(id="theme_form"):
                yield Static("Create New Theme", classes="title")
                yield Input(placeholder="Theme Name", id="theme_name")
                yield Static("Theme Colors", classes="section_title")
                with Vertical():
                    for label, key in [
                        ("Primary", "primary"),
                        ("Secondary", "secondary"),
                        ("Accent", "accent"),
                        ("Foreground", "foreground"),
                        ("Background", "background"),
                        ("Success", "success"),
                        ("Warning", "warning"),
                        ("Error", "error"),
                        ("Surface", "surface"),
                        ("Panel", "panel")
                    ]:
                        with Horizontal():
                            yield Static(label, classes="color_label")
                            yield Input(value=self.theme_data[key], id=f"color_{key}")
                            yield Static("", classes="color_preview", id=f"preview_{key}")
                with Horizontal(id="button_container"):
                    yield Button("Save Theme", id="save_theme")
                    yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        self.logger.info("Theme creation screen mounted")
        self._update_color_previews()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "theme_name":
            self.theme_name = event.value
            event.input.value = self.theme_name
        elif event.input.id.startswith("color_"):
            color_key = event.input.id.replace("color_", "")
            color_value = event.value.strip()
            if color_value == "":
                self.theme_data[color_key] = ""
                event.input.value = ""
                return
            if not color_value.startswith('#'):
                color_value = '#' + color_value
            if self._is_valid_color(color_value):
                self.theme_data[color_key] = color_value
                self._update_color_preview(color_key)
                event.input.value = color_value
            else:
                self.notify(f"Invalid color format. Please use hex color codes (e.g., #ff0000)", severity="error")

    def _is_valid_color(self, color: str) -> bool:
        return bool(self.color_pattern.match(color))

    def _update_color_previews(self) -> None:
        for color_key in self.theme_data.keys():
            if color_key != "name" and color_key != "dark":
                self._update_color_preview(color_key)

    def _update_color_preview(self, color_key: str) -> None:
        try:
            preview = self.query_one(f"#preview_{color_key}", Static)
            preview.styles.background = self.theme_data[color_key]
        except Exception as e:
            self.logger.error(f"Error updating color preview: {str(e)}", exc_info=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_theme":
            self._save_theme()
        elif event.button.id == "cancel":
            self.parent_content.remove_children()
            post_list = PostList(posts=self.current_posts, id="content")
            self.parent_content.mount(post_list)
            self.app.active_widget = "content"
            post_list.focus()

    def _save_theme(self) -> None:
        if not self.theme_name:
            self.notify("Please enter a theme name", severity="error")
            return
        for key, value in self.theme_data.items():
            if key not in ["name", "dark"] and not self._is_valid_color(value):
                self.notify(f"Invalid color format for {key}. Please use hex color codes (e.g., #ff0000)", severity="error")
                return
        self.theme_data["name"] = self.theme_name
        theme_path = os.path.join("themes", f"{self.theme_name.lower()}.theme")
        try:
            with open(theme_path, "w") as f:
                json.dump(self.theme_data, f, indent=4)
            self.notify("Theme saved successfully!", severity="success")
            self.parent_content.remove_children()
            post_list = PostList(posts=self.current_posts, id="content")
            self.parent_content.mount(post_list)
            self.app.active_widget = "content"
            post_list.focus()
        except Exception as e:
            self.logger.error(f"Error saving theme: {str(e)}", exc_info=True)
            self.notify(f"Error saving theme: {str(e)}", severity="error") 