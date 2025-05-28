import os
import json

class Settings:
    def __init__(self):
        self.theme = "Default"
        self.posts_per_page = 25
        self.comment_depth = 50
        self.auto_load_comments = True
        self.show_nsfw = True
    
    def load_settings_from_file(self):
        settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings.json")
        try:
            if os.path.exists(settings_path):
                with open(settings_path, "r") as settingsfile:
                    settings = json.load(settingsfile)
                    self.theme = str(settings.get("theme", self.theme))
                    self.posts_per_page = int(settings.get("posts_per_page", self.posts_per_page))
                    self.comment_depth = int(settings.get("comment_depth", self.comment_depth))
                    self.auto_load_comments = str(settings.get("auto_load_comments", str(self.auto_load_comments))).lower() == "true"
                    self.show_nsfw = str(settings.get("show_nsfw", str(self.show_nsfw))).lower() == "true"
            else:
                self.save_settings_to_file()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.save_settings_to_file()

    def save_settings_to_file(self):
        settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings.json")
        try:
            settings = {
                "theme": self.theme,
                "posts_per_page": str(self.posts_per_page),
                "comment_depth": str(self.comment_depth),
                "auto_load_comments": str(self.auto_load_comments),
                "show_nsfw": str(self.show_nsfw)
            }
            with open(settings_path, "w") as settingsfile:
                json.dump(settings, settingsfile, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")