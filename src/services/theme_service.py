import json
import os
from rich.style import Style

class ThemeService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeService, cls).__new__(cls)
            cls._instance._initialize_themes()
        return cls._instance

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

    def get_style(self, style_name):
        if style_name in self.themes[self.current_theme]:
            return self.themes[self.current_theme][style_name]
        return "#ffffff"  # Default fallback color

    def set_theme(self, theme_name):
        if theme_name.lower() in self.themes:
            self.current_theme = theme_name.lower()
            return True
        return False

    def get_available_themes(self):
        return list(self.themes.keys())

    def get_current_theme(self):
        return self.current_theme

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