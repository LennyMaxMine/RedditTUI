import os
import json
from utils.logger import Logger

class Settings:
    def __init__(self):
        self.logger = Logger()
        self.settings_file = "settings.json"
        self.default_settings = {
            "posts_per_page": 25,
            "comment_depth": 3,
            "auto_load_comments": True,
            "show_nsfw": False,
            "theme": "default",
            "sort_comments_by": "best"
        }
        self.settings = self.default_settings.copy()
        self.logger.info("Settings service initialized")

    def load_settings_from_file(self):
        try:
            if os.path.exists(self.settings_file):
                self.logger.info(f"Loading settings from {self.settings_file}")
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
                    self.logger.info("Settings loaded successfully")
            else:
                self.logger.info("No settings file found, using defaults")
                self.save_settings_to_file()
        except Exception as e:
            error_msg = f"Error loading settings: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.settings = self.default_settings.copy()

    def save_settings_to_file(self):
        try:
            self.logger.info(f"Saving settings to {self.settings_file}")
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            self.logger.info("Settings saved successfully")
        except Exception as e:
            error_msg = f"Error saving settings: {str(e)}"
            self.logger.error(error_msg, exc_info=True)

    def get_setting(self, key):
        self.logger.debug(f"Getting setting: {key}")
        return self.settings.get(key, self.default_settings.get(key))

    def set_setting(self, key, value):
        self.logger.info(f"Setting {key} to {value}")
        self.settings[key] = value
        self.save_settings_to_file()

    def reset_to_defaults(self):
        self.logger.info("Resetting settings to defaults")
        self.settings = self.default_settings.copy()
        self.save_settings_to_file()

    def apply_settings(self):
        self.logger.info("Applying settings")
        # Add any runtime settings application logic here
        pass