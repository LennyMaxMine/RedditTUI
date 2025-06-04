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
        # Remove duplicate initialization
        pass

    def _initialize_themes(self):
        self.logger = Logger()
        self.themes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'themes')
        self.themes = {}
        self.current_theme = "default"
        
        # First load custom themes from JSON files
        self.load_custom_themes()
        
        # Then add default themes if they don't exist
        if "default" not in self.themes:
            self.themes["default"] = {
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
            }
        
        if "dark" not in self.themes:
            self.themes["dark"] = {
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
            }
        
        if "light" not in self.themes:
            self.themes["light"] = {
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
        
        # Finally load theme from settings
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
                            theme_data = json.load(f)
                            # Handle both nested and flat theme structures
                            if 'colors' in theme_data:
                                self.themes[theme_name] = theme_data['colors']
                            else:
                                self.themes[theme_name] = theme_data
                        self.logger.info(f"Loaded theme: {theme_name}")
                    except Exception as e:
                        error_msg = f"Error loading theme {theme_name}: {str(e)}"
                        self.logger.error(error_msg, exc_info=True)
        except Exception as e:
            error_msg = f"Error loading themes: {str(e)}"
            self.logger.error(error_msg, exc_info=True)

    def get_theme(self, theme_name):
        self.logger.debug(f"Getting theme: {theme_name}")
        theme = self.themes.get(theme_name)
        if not theme:
            self.logger.warning(f"Theme {theme_name} not found, falling back to default")
            theme = self.themes.get('default', {})
        return theme

    def set_theme(self, theme_name):
        self.logger.info(f"Setting theme to: {theme_name}")
        # Convert theme name to lowercase for case-insensitive comparison
        theme_name_lower = theme_name.lower()
        # Find the actual theme name with correct case
        actual_theme_name = next((name for name in self.themes.keys() if name.lower() == theme_name_lower), None)
        if actual_theme_name:
            self.current_theme = actual_theme_name
            return True
        self.logger.warning(f"Theme not found: {theme_name}, falling back to default")
        self.current_theme = "default"
        return False

    def get_style(self, style_name):
        self.logger.debug(f"Getting style {style_name} from theme {self.current_theme}")
        theme = self.get_theme(self.current_theme)
        color = theme.get(style_name)
        if not color:
            self.logger.warning(f"Style {style_name} not found in theme {self.current_theme}, falling back to default")
            default_theme = self.get_theme('default')
            color = default_theme.get(style_name, '#ffffff')  # Default to white if style not found
        return color

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
                    error_msg = f"Error loading theme {theme_file}: {e}"
                    self.logger.error(error_msg, exc_info=True)

    def load_theme_from_settings(self):
        settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'settings.json')
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    if 'theme' in settings:
                        # Convert theme name to lowercase for case-insensitive comparison
                        theme_name = settings['theme']
                        theme_name_lower = theme_name.lower()
                        # Find the actual theme name with correct case
                        actual_theme_name = next((name for name in self.themes.keys() if name.lower() == theme_name_lower), None)
                        if actual_theme_name:
                            self.set_theme(actual_theme_name)
                        else:
                            self.logger.warning(f"Theme not found in settings: {theme_name}")
        except Exception as e:
            error_msg = f"Error loading theme from settings: {e}"
            self.logger.error(error_msg, exc_info=True)

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
            error_msg = f"Error creating theme: {e}"
            self.logger.error(error_msg, exc_info=True)
            return False 