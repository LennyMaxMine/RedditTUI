import json
import os
from rich.style import Style
from utils.logger import Logger

class ThemeService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeService, cls).__new__(cls)
            cls._instance._initialize_themes()
        return cls._instance

    def __init__(self):
        self.logger = Logger()
        self.themes_dir = "themes"
        self.current_theme = "default"
        self.themes = {}
        self.logger.info("Theme service initialized")
        self.load_themes()

    def _initialize_themes(self):
        self.themes = {
            "default": {
                "title": "#00ffff",
                "subreddit": "#00ff00",
                "author": "#ffff00",
                "score": "#ff00ff",
                "comments": "#0000ff",
                "content": "#ffffff",
                "sidebar": "#00ffff",
                "sidebar_item": "#ffffff",
                "panel_title": "#00ffff",
                "error": "#ff0000",
                "success": "#00ff00",
                "warning": "#ffff00",
                "info": "#00ffff",
                "highlight": "#ff00ff"
            },
            "dark": {
                "title": "#4ec9b0",
                "subreddit": "#9cdcfe",
                "author": "#dcdcaa",
                "score": "#ce9178",
                "comments": "#569cd6",
                "content": "#d4d4d4",
                "sidebar": "#4ec9b0",
                "sidebar_item": "#d4d4d4",
                "panel_title": "#4ec9b0",
                "error": "#f44747",
                "success": "#6a9955",
                "warning": "#dcdcaa",
                "info": "#4ec9b0",
                "highlight": "#ce9178"
            },
            "light": {
                "title": "#008080",
                "subreddit": "#008000",
                "author": "#808000",
                "score": "#800080",
                "comments": "#000080",
                "content": "#000000",
                "sidebar": "#008080",
                "sidebar_item": "#000000",
                "panel_title": "#008080",
                "error": "#ff0000",
                "success": "#008000",
                "warning": "#808000",
                "info": "#008080",
                "highlight": "#800080"
            }
        }
        self.current_theme = "default"
        self.load_custom_themes()
        self.load_theme_from_settings()

    def load_themes(self):
        try:
            self.logger.info("Loading themes")
            if not os.path.exists(self.themes_dir):
                self.logger.warning(f"Themes directory not found: {self.themes_dir}")
                return

            for filename in os.listdir(self.themes_dir):
                if filename.endswith('.json'):
                    theme_name = filename[:-5]
                    theme_path = os.path.join(self.themes_dir, filename)
                    try:
                        with open(theme_path, 'r') as f:
                            self.themes[theme_name] = json.load(f)
                        self.logger.info(f"Loaded theme: {theme_name}")
                    except Exception as e:
                        error_msg = f"Error loading theme {theme_name}: {str(e)}"
                        self.logger.error(error_msg, exc_info=True)
        except Exception as e:
            error_msg = f"Error loading themes: {str(e)}"
            self.logger.error(error_msg, exc_info=True)

    def get_theme(self, theme_name):
        self.logger.debug(f"Getting theme: {theme_name}")
        return self.themes.get(theme_name, self.themes.get('default', {}))

    def set_theme(self, theme_name):
        self.logger.info(f"Setting theme to: {theme_name}")
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        self.logger.warning(f"Theme not found: {theme_name}")
        return False

    def get_style(self, style_name):
        self.logger.debug(f"Getting style {style_name} from theme {self.current_theme}")
        theme = self.get_theme(self.current_theme)
        return theme.get(style_name, '#000000')  # Default to black if style not found

    def get_available_themes(self):
        self.logger.debug("Getting available themes")
        return list(self.themes.keys())

    def get_current_theme(self):
        return self.current_theme

    def create_theme(self, theme_name, theme_data):
        try:
            self.logger.info(f"Creating new theme: {theme_name}")
            if not os.path.exists(self.themes_dir):
                os.makedirs(self.themes_dir)
            
            theme_path = os.path.join(self.themes_dir, f"{theme_name}.json")
            with open(theme_path, 'w') as f:
                json.dump(theme_data, f, indent=4)
            self.themes[theme_name] = theme_data
            self.logger.info(f"Theme created successfully: {theme_name}")
            return True
        except Exception as e:
            error_msg = f"Error creating theme {theme_name}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return False

    def delete_theme(self, theme_name):
        try:
            self.logger.info(f"Deleting theme: {theme_name}")
            if theme_name == 'default':
                self.logger.warning("Cannot delete default theme")
                return False
            
            theme_path = os.path.join(self.themes_dir, f"{theme_name}.json")
            if os.path.exists(theme_path):
                os.remove(theme_path)
                del self.themes[theme_name]
                self.logger.info(f"Theme deleted successfully: {theme_name}")
                return True
            self.logger.warning(f"Theme file not found: {theme_name}")
            return False
        except Exception as e:
            error_msg = f"Error deleting theme {theme_name}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return False

    def load_custom_themes(self):
        themes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'themes')
        if not os.path.exists(themes_dir):
            os.makedirs(themes_dir)
            return

        for theme_file in os.listdir(themes_dir):
            if theme_file.endswith('.json'):
                try:
                    with open(os.path.join(themes_dir, theme_file), 'r') as f:
                        theme_data = json.load(f)
                        theme_name = theme_data.get('name', theme_file[:-5]).lower()
                        colors = theme_data.get('colors', {})
                        self.themes[theme_name] = colors
                except Exception as e:
                    print(f"Error loading theme {theme_file}: {e}")

    def load_theme_from_settings(self):
        settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'settings.json')
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    if 'theme' in settings:
                        self.set_theme(settings['theme'].lower())
        except Exception as e:
            print(f"Error loading theme from settings: {e}")

    def create_custom_theme(self, name, colors):
        themes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'themes')
        if not os.path.exists(themes_dir):
            os.makedirs(themes_dir)

        theme_data = {
            "name": name,
            "description": f"Custom theme: {name}",
            "colors": colors
        }

        theme_file = os.path.join(themes_dir, f"{name.lower()}.json")
        try:
            with open(theme_file, 'w') as f:
                json.dump(theme_data, f, indent=4)
            self.load_custom_themes()
            return True
        except Exception as e:
            print(f"Error creating theme: {e}")
            return False 