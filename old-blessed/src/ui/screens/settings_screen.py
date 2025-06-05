from blessed import Terminal
import json
import os
import time
from ui.screens.login_screen import LoginScreen
from ui.screens.theme_screen import ThemeScreen
from services.theme_service import ThemeService
from utils.logger import Logger
import sys

class SettingsScreen:
    def __init__(self, terminal):
        self.terminal = terminal
        self.theme_service = ThemeService()
        self.logger = Logger()
        self.selected_option = 0
        self.settings_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'settings.json')
        self.settings = self.load_settings()
        self.options = [
            ("Theme", self.settings["theme"]),
            ("Posts per page", self.settings["posts_per_page"]),
            ("Comment depth", self.settings["comment_depth"]),
            ("Auto load comments", self.settings["auto_load_comments"]),
            ("Show NSFW content", self.settings["show_nsfw"]),
            ("Spinner refresh rate (ms)", self.settings["spinner_refresh_rate"])
        ]
        self.posts_per_page_options = ["10", "25", "50", "100", "250", "500"]
        self.comment_depth_options = ["1", "2", "3", "4", "5", "25", "50", "100"]
        self.boolean_options = ["True", "False"]
        self.spinner_refresh_rate_options = ["50", "100", "200", "500", "1000"]
        self.message = None
        self.message_time = 0
        self.login_screen = LoginScreen(None)
        self.theme_screen = ThemeScreen(terminal)
        self.theme_screen.themes = self.theme_service.get_available_themes()
        self.theme_screen.current_theme = self.theme_service.get_current_theme()
        self.reddit_instance = None
        self.theme_screen_activated = False
        self.logger.info("Settings screen initialized")

    def show_message(self, message, is_error=False):
        self.message = message
        self.message_time = time.time()
        self.is_error = is_error
        if is_error:
            self.logger.error(message)
        else:
            self.logger.info(message)

    def load_settings(self):
        default_settings = {
            "theme": "Default",
            "posts_per_page": "25",
            "comment_depth": "3",
            "auto_load_comments": "True",
            "show_nsfw": "False",
            "spinner_refresh_rate": "500"
        }
        
        try:
            if os.path.exists(self.settings_file):
                self.logger.info(f"Loading settings from {self.settings_file}")
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    for key, value in default_settings.items():
                        if key not in loaded_settings:
                            loaded_settings[key] = value
                    self.logger.info("Settings loaded successfully")
                    return loaded_settings
            else:
                self.logger.info("No settings file found, creating with defaults")
                with open(self.settings_file, 'w') as f:
                    json.dump(default_settings, f, indent=4)
                return default_settings
        except Exception as e:
            error_msg = f"Error loading settings: {e}"
            self.show_message(error_msg, True)
            self.logger.error(error_msg, exc_info=True)
            return default_settings

    def save_settings(self):
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            self.logger.info(f"Saving settings to {self.settings_file}")
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            self.theme_service.set_theme(self.settings["theme"].lower())
            self.show_message("Settings saved successfully!")
            self.logger.info("Settings saved successfully")
            return True
        except Exception as e:
            error_msg = f"Error saving settings: {e}"
            self.show_message(error_msg, True)
            self.logger.error(error_msg, exc_info=True)
            return False

    def display(self):
        if self.theme_screen_activated:  # Only show theme screen if explicitly activated
            return self.theme_screen.get_display()

        width = self.terminal.width - 22
        output = []
        
        output.append(f"┬{'─' * (width-2)}┤")
        output.append(f"│{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('Settings').center(width+22)}│")
        
        for idx, option in enumerate(self.options):
            if idx == self.selected_option:
                prefix = self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('highlight')))("│ ► ")
            else:
                prefix = "│   "

            output.append(f"├{'─' * (width-2)}┤")

            if prefix != "│   ":
                output.append(f"{prefix}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('title')))(option[0])}".ljust(width+46) + "│")
            else:
                output.append(f"{prefix}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('title')))(option[0])}".ljust(width+23) + "│")
            
            if option[0] == "Login":
                if self.reddit_instance:
                    output.append(f"│    {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('success')))('Logged in as: ' + self.reddit_instance.user.me().name)}".ljust(width+20) + "│")
                else:
                    output.append(f"│    {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('error')))('Not logged in')}".ljust(width+10) + "│")
                output.append(f"│    {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('info')))('Press Enter to login/logout')}".ljust(width+22) + "│")
            
            elif option[0] == "Theme":
                output.append(f"│    {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('info')))('Press Enter to select theme')}".ljust(width+22) + "│")
                output.append(f"│    {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('Current theme: ' + option[1])}".ljust(width+24) + "│")
            
            elif option[0] == "Posts per page":
                options_line = "│    "
                for count in self.posts_per_page_options:
                    if count == option[1]:
                        options_line += self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('highlight')))(f"[{count}] ")
                    else:
                        options_line += self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(f"{count} ")
                output.append(f"{options_line}".ljust(width+147) + "│")
            
            elif option[0] == "Comment depth":
                options_line = "│    "
                for depth in self.comment_depth_options:
                    if depth == option[1]:
                        options_line += self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('highlight')))(f"[{depth}] ")
                    else:
                        options_line += self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(f"{depth} ")
                output.append(f"{options_line}".ljust(width+197) + "│")
            
            elif option[0] == "Auto load comments":
                options_line = "│    "
                for value in self.boolean_options:
                    if value == option[1]:
                        options_line += self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('highlight')))(f"[{value}] ")
                    else:
                        options_line += self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(f"{value} ")
                output.append(f"{options_line}".ljust(width+47) + "│")
            
            elif option[0] == "Show NSFW content":
                options_line = "│    "
                for value in self.boolean_options:
                    if value == option[1]:
                        options_line += self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('highlight')))(f"[{value}] ")
                    else:
                        options_line += self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(f"{value} ")
                output.append(f"{options_line}".ljust(width+47) + "│")
            
            elif option[0] == "Spinner refresh rate (ms)":
                options_line = "│    "
                for rate in self.spinner_refresh_rate_options:
                    if rate == option[1]:
                        options_line += self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('highlight')))(f"[{rate}] ")
                    else:
                        options_line += self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(f"{rate} ")
                output.append(f"{options_line}".ljust(width+147) + "│")
            
            elif option[0] == "Save Settings":
                output.append(f"│    {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('info')))('Press Enter to save current settings')}".ljust(width+22) + "│")

        output.append(f"╰{'─' * (width-2)}╯")
        
        output.append(f"")
        output.append(f"╭{'─' * (width-2)}╮")
        output.append(f"│{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('info')))('Instructions:').center(width+21)}│")
        output.append(f"│    {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• Up/Down Arrow: Navigate options')}".ljust(width+24) + "│")
        output.append(f"│    {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• Left/Right Arrow: Change values')}".ljust(width+24) + "│")
        output.append(f"│    {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• Enter: Save settings / Login')}".ljust(width+24) + "│")
        output.append(f"│    {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• Escape: Return without saving')}".ljust(width+24) + "│")
        output.append(f"╰{'─' * (width-2)}╯")

        if self.message and time.time() - self.message_time < 3:
            message_color = self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('error'))) if self.is_error else self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('success')))
            output.append(f"╭{'─' * (width-2)}╮")
            output.append(f"│{message_color(self.message).center(width+9)}│")
            output.append(f"╰{'─' * (width-2)}╯")
        
        return "\n".join(output)

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def handle_enter(self):
        if self.selected_option == 0:  # Theme
            self.logger.info("Activating theme screen")
            self.theme_screen_activated = True
            return False
        elif self.selected_option == 1:  # Posts per page
            current_idx = self.posts_per_page_options.index(self.settings["posts_per_page"])
            self.settings["posts_per_page"] = self.posts_per_page_options[(current_idx + 1) % len(self.posts_per_page_options)]
            self.logger.info(f"Changed posts per page to {self.settings['posts_per_page']}")
            self.save_settings()
            return False
        elif self.selected_option == 2:  # Comment depth
            current_idx = self.comment_depth_options.index(self.settings["comment_depth"])
            self.settings["comment_depth"] = self.comment_depth_options[(current_idx + 1) % len(self.comment_depth_options)]
            self.logger.info(f"Changed comment depth to {self.settings['comment_depth']}")
            self.save_settings()
            return False
        elif self.selected_option == 3:  # Auto load comments
            current_idx = self.boolean_options.index(self.settings["auto_load_comments"])
            self.settings["auto_load_comments"] = self.boolean_options[(current_idx + 1) % len(self.boolean_options)]
            self.logger.info(f"Changed auto load comments to {self.settings['auto_load_comments']}")
            self.save_settings()
            return False
        elif self.selected_option == 4:  # Show NSFW content
            current_idx = self.boolean_options.index(self.settings["show_nsfw"])
            self.settings["show_nsfw"] = self.boolean_options[(current_idx + 1) % len(self.boolean_options)]
            self.logger.info(f"Changed show NSFW content to {self.settings['show_nsfw']}")
            self.save_settings()
            return False
        elif self.selected_option == 5:  # Spinner refresh rate
            current_idx = self.spinner_refresh_rate_options.index(self.settings["spinner_refresh_rate"])
            self.settings["spinner_refresh_rate"] = self.spinner_refresh_rate_options[(current_idx + 1) % len(self.spinner_refresh_rate_options)]
            self.logger.info(f"Changed spinner refresh rate to {self.settings['spinner_refresh_rate']}")
            self.save_settings()
            return False
        return False

    def theme_scroll_up(self):
        if self.theme_screen_activated:
            self.logger.debug("Scrolling theme screen up")
            self.theme_screen.scroll_up()

    def theme_scroll_down(self):
        if self.theme_screen_activated:
            self.logger.debug("Scrolling theme screen down")
            self.theme_screen.scroll_down()

    def handle_input(self, key):
        if self.theme_screen_activated:
            if key == '\x1b[A':  # Up Arrow
                self.theme_screen.scroll_up()
                return False
            elif key == '\x1b[B':  # Down Arrow
                self.theme_screen.scroll_down()
                return False
            elif key in ['\r', '\n', '\x0a', '\x0d', '\x1b\x0d', '\x1b\x0a']:  # Enter
                selected_theme = self.theme_screen.select_theme()
                if selected_theme:
                    self.logger.info(f"Selected theme: {selected_theme}")
                    self.settings["theme"] = selected_theme
                    self.theme_service.set_theme(selected_theme.lower())
                    self.theme_screen_activated = False
                    self.save_settings()
                    return True
            elif key == '\x1b':  # Escape
                self.logger.info("Exiting theme screen")
                self.theme_screen_activated = False
                return False
            return False
        else:
            if key == '\x1b[A':  # Up Arrow
                self.previous_option()
                self.logger.debug(f"Selected option: {self.options[self.selected_option][0]}")
                return False
            elif key == '\x1b[B':  # Down Arrow
                self.next_option()
                self.logger.debug(f"Selected option: {self.options[self.selected_option][0]}")
                return False
            elif key == '\x1b[C':  # Right Arrow
                if self.selected_option == 0:  # Theme
                    self.logger.info("Activating theme screen")
                    self.theme_screen_activated = True
                    return False
                elif self.selected_option == 1:  # Posts Per Page
                    current_idx = self.posts_per_page_options.index(self.settings["posts_per_page"])
                    self.settings["posts_per_page"] = self.posts_per_page_options[(current_idx + 1) % len(self.posts_per_page_options)]
                    self.logger.info(f"Changed posts per page to {self.settings['posts_per_page']}")
                    self.save_settings()
                elif self.selected_option == 2:  # Comment Depth
                    current_idx = self.comment_depth_options.index(self.settings["comment_depth"])
                    self.settings["comment_depth"] = self.comment_depth_options[(current_idx + 1) % len(self.comment_depth_options)]
                    self.logger.info(f"Changed comment depth to {self.settings['comment_depth']}")
                    self.save_settings()
                elif self.selected_option == 3:  # Auto Load Comments
                    current_idx = self.boolean_options.index(self.settings["auto_load_comments"])
                    self.settings["auto_load_comments"] = self.boolean_options[(current_idx + 1) % len(self.boolean_options)]
                    self.logger.info(f"Changed auto load comments to {self.settings['auto_load_comments']}")
                    self.save_settings()
                elif self.selected_option == 4:  # Show NSFW Content
                    current_idx = self.boolean_options.index(self.settings["show_nsfw"])
                    self.settings["show_nsfw"] = self.boolean_options[(current_idx + 1) % len(self.boolean_options)]
                    self.logger.info(f"Changed show NSFW content to {self.settings['show_nsfw']}")
                    self.save_settings()
                elif self.selected_option == 5:  # Spinner Refresh Rate
                    current_idx = self.spinner_refresh_rate_options.index(self.settings["spinner_refresh_rate"])
                    self.settings["spinner_refresh_rate"] = self.spinner_refresh_rate_options[(current_idx + 1) % len(self.spinner_refresh_rate_options)]
                    self.logger.info(f"Changed spinner refresh rate to {self.settings['spinner_refresh_rate']}")
                    self.save_settings()
                return False
            elif key == '\x1b[D':  # Left Arrow
                if self.selected_option == 0:  # Theme
                    self.logger.info("Activating theme screen")
                    self.theme_screen_activated = True
                    return False
                elif self.selected_option == 1:  # Posts Per Page
                    current_idx = self.posts_per_page_options.index(self.settings["posts_per_page"])
                    self.settings["posts_per_page"] = self.posts_per_page_options[(current_idx - 1) % len(self.posts_per_page_options)]
                    self.logger.info(f"Changed posts per page to {self.settings['posts_per_page']}")
                    self.save_settings()
                elif self.selected_option == 2:  # Comment Depth
                    current_idx = self.comment_depth_options.index(self.settings["comment_depth"])
                    self.settings["comment_depth"] = self.comment_depth_options[(current_idx - 1) % len(self.comment_depth_options)]
                    self.logger.info(f"Changed comment depth to {self.settings['comment_depth']}")
                    self.save_settings()
                elif self.selected_option == 3:  # Auto Load Comments
                    current_idx = self.boolean_options.index(self.settings["auto_load_comments"])
                    self.settings["auto_load_comments"] = self.boolean_options[(current_idx - 1) % len(self.boolean_options)]
                    self.logger.info(f"Changed auto load comments to {self.settings['auto_load_comments']}")
                    self.save_settings()
                elif self.selected_option == 4:  # Show NSFW Content
                    current_idx = self.boolean_options.index(self.settings["show_nsfw"])
                    self.settings["show_nsfw"] = self.boolean_options[(current_idx - 1) % len(self.boolean_options)]
                    self.logger.info(f"Changed show NSFW content to {self.settings['show_nsfw']}")
                    self.save_settings()
                elif self.selected_option == 5:  # Spinner Refresh Rate
                    current_idx = self.spinner_refresh_rate_options.index(self.settings["spinner_refresh_rate"])
                    self.settings["spinner_refresh_rate"] = self.spinner_refresh_rate_options[(current_idx - 1) % len(self.spinner_refresh_rate_options)]
                    self.logger.info(f"Changed spinner refresh rate to {self.settings['spinner_refresh_rate']}")
                    self.save_settings()
                return False
            elif key == '\t':  # Tab
                return self.next_value()
            elif key in ['\r', '\n', '\x0a', '\x0d', '\x1b\x0d', '\x1b\x0a']:  # Enter
                return self.handle_enter()
            elif key == '\x1b':  # Escape
                self.logger.info("Exiting settings screen")
                return True
            return False

    def next_option(self):
        self.selected_option = (self.selected_option + 1) % len(self.options)
        self.logger.debug(f"Selected option: {self.options[self.selected_option][0]}")

    def previous_option(self):
        self.selected_option = (self.selected_option - 1) % len(self.options)
        self.logger.debug(f"Selected option: {self.options[self.selected_option][0]}")

    def next_value(self):
        if self.selected_option == 0:  # Theme
            return False
        elif self.selected_option == 1:  # Posts Per Page
            current_idx = self.posts_per_page_options.index(self.settings["posts_per_page"])
            self.settings["posts_per_page"] = self.posts_per_page_options[(current_idx + 1) % len(self.posts_per_page_options)]
            self.logger.info(f"Changed posts per page to {self.settings['posts_per_page']}")
            self.save_settings()
        elif self.selected_option == 2:  # Comment Depth
            current_idx = self.comment_depth_options.index(self.settings["comment_depth"])
            self.settings["comment_depth"] = self.comment_depth_options[(current_idx + 1) % len(self.comment_depth_options)]
            self.logger.info(f"Changed comment depth to {self.settings['comment_depth']}")
            self.save_settings()
        elif self.selected_option == 3:  # Auto Load Comments
            current_idx = self.boolean_options.index(self.settings["auto_load_comments"])
            self.settings["auto_load_comments"] = self.boolean_options[(current_idx + 1) % len(self.boolean_options)]
            self.logger.info(f"Changed auto load comments to {self.settings['auto_load_comments']}")
            self.save_settings()
        elif self.selected_option == 4:  # Show NSFW Content
            current_idx = self.boolean_options.index(self.settings["show_nsfw"])
            self.settings["show_nsfw"] = self.boolean_options[(current_idx + 1) % len(self.boolean_options)]
            self.logger.info(f"Changed show NSFW content to {self.settings['show_nsfw']}")
            self.save_settings()
        elif self.selected_option == 5:  # Spinner Refresh Rate
            current_idx = self.spinner_refresh_rate_options.index(self.settings["spinner_refresh_rate"])
            self.settings["spinner_refresh_rate"] = self.spinner_refresh_rate_options[(current_idx + 1) % len(self.spinner_refresh_rate_options)]
            self.logger.info(f"Changed spinner refresh rate to {self.settings['spinner_refresh_rate']}")
            self.save_settings()
        return False

    def previous_value(self):
        if self.selected_option == 0:  # Theme
            return False
        elif self.selected_option == 1:  # Posts Per Page
            current_idx = self.posts_per_page_options.index(self.settings["posts_per_page"])
            self.settings["posts_per_page"] = self.posts_per_page_options[(current_idx - 1) % len(self.posts_per_page_options)]
            self.logger.info(f"Changed posts per page to {self.settings['posts_per_page']}")
            self.save_settings()
        elif self.selected_option == 2:  # Comment Depth
            current_idx = self.comment_depth_options.index(self.settings["comment_depth"])
            self.settings["comment_depth"] = self.comment_depth_options[(current_idx - 1) % len(self.comment_depth_options)]
            self.logger.info(f"Changed comment depth to {self.settings['comment_depth']}")
            self.save_settings()
        elif self.selected_option == 3:  # Auto Load Comments
            current_idx = self.boolean_options.index(self.settings["auto_load_comments"])
            self.settings["auto_load_comments"] = self.boolean_options[(current_idx - 1) % len(self.boolean_options)]
            self.logger.info(f"Changed auto load comments to {self.settings['auto_load_comments']}")
            self.save_settings()
        elif self.selected_option == 4:  # Show NSFW Content
            current_idx = self.boolean_options.index(self.settings["show_nsfw"])
            self.settings["show_nsfw"] = self.boolean_options[(current_idx - 1) % len(self.boolean_options)]
            self.logger.info(f"Changed show NSFW content to {self.settings['show_nsfw']}")
            self.save_settings()
        elif self.selected_option == 5:  # Spinner Refresh Rate
            current_idx = self.spinner_refresh_rate_options.index(self.settings["spinner_refresh_rate"])
            self.settings["spinner_refresh_rate"] = self.spinner_refresh_rate_options[(current_idx - 1) % len(self.spinner_refresh_rate_options)]
            self.logger.info(f"Changed spinner refresh rate to {self.settings['spinner_refresh_rate']}")
            self.save_settings()
        return False 