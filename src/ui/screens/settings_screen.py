from blessed import Terminal
import json
import os
import time
from ui.screens.login_screen import LoginScreen

class SettingsScreen:
    def __init__(self, terminal):
        self.terminal = terminal
        self.selected_option = 0
        self.settings_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'settings.json')
        self.settings = self.load_settings()
        self.options = [
            "Login",
            "Theme",
            "Posts Per Page",
            "Comment Depth",
            "Auto Load Comments",
            "Show NSFW Content",
            "Save Settings"
        ]
        self.themes = ["Default", "Dark", "Light"]
        self.posts_per_page_options = ["10", "25", "50", "100", "250", "500"]
        self.comment_depth_options = ["1", "2", "3", "4", "5"]
        self.boolean_options = ["True", "False"]
        self.message = None
        self.message_time = 0
        self.login_screen = LoginScreen(None)
        self.reddit_instance = None

    def show_message(self, message, is_error=False):
        self.message = message
        self.message_time = time.time()
        self.is_error = is_error

    def load_settings(self):
        default_settings = {
            "theme": "Default",
            "posts_per_page": "25",
            "comment_depth": "3",
            "auto_load_comments": "True",
            "show_nsfw": "False"
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    for key, value in default_settings.items():
                        if key not in loaded_settings:
                            loaded_settings[key] = value
                    return loaded_settings
            else:
                with open(self.settings_file, 'w') as f:
                    json.dump(default_settings, f, indent=4)
                return default_settings
        except Exception as e:
            self.show_message(f"Error loading settings: {e}", True)
            return default_settings

    def save_settings(self):
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            self.show_message("Settings saved successfully!")
            return True
        except Exception as e:
            self.show_message(f"Error saving settings: {e}", True)
            return False

    def display(self):
        width = self.terminal.width - 22
        output = []
        
        output.append(f"┬{'─' * (width-2)}┤")
        output.append(f"│{self.terminal.bright_blue('Settings').center(width+9)}│")
        #output.append(f"├{'─' * (width-2)}┤")
        
        for idx, option in enumerate(self.options):
            if idx == self.selected_option:
                prefix = self.terminal.bright_green("│ ► ")
            else:
                prefix = "│   "

            output.append(f"├{'─' * (width-2)}┤")


            if prefix != "│   ":
                output.append(f"{prefix}{self.terminal.bold_white(option)}".ljust(width+25) + "│")
            else:
                output.append(f"{prefix}{self.terminal.bold_white(option)}".ljust(width+14) + "│")
            
            if option == "Login":
                if self.reddit_instance:
                    output.append(f"│    {self.terminal.green('Logged in as: ' + self.reddit_instance.user.me().name)}".ljust(width+10) + "│")
                else:
                    output.append(f"│    {self.terminal.red('Not logged in')}".ljust(width+10) + "│")
                output.append(f"│    {self.terminal.cyan('Press Enter to login/logout')}".ljust(width+10) + "│")
            
            elif option == "Theme":
                options_line = "│    "
                for theme in self.themes:
                    if theme == self.settings["theme"]:
                        options_line += self.terminal.bright_green(f"[{theme}] ")
                    else:
                        options_line += self.terminal.white(f"{theme} ")
                output.append(f"{options_line}".ljust(width+32) + "│")
            
            elif option == "Posts Per Page":
                options_line = "│    "
                for count in self.posts_per_page_options:
                    if count == self.settings["posts_per_page"]:
                        options_line += self.terminal.bright_green(f"[{count}] ")
                    else:
                        options_line += self.terminal.white(f"{count} ")
                output.append(f"{options_line}".ljust(width+65) + "│")
            
            elif option == "Comment Depth":
                options_line = "│    "
                for depth in self.comment_depth_options:
                    if depth == self.settings["comment_depth"]:
                        options_line += self.terminal.bright_green(f"[{depth}] ")
                    else:
                        options_line += self.terminal.white(f"{depth} ")
                output.append(f"{options_line}".ljust(width+54) + "│")
            
            elif option == "Auto Load Comments":
                options_line = "│    "
                for value in self.boolean_options:
                    if value == self.settings["auto_load_comments"]:
                        options_line += self.terminal.bright_green(f"[{value}] ")
                    else:
                        options_line += self.terminal.white(f"{value} ")
                output.append(f"{options_line}".ljust(width+21) + "│")
            
            elif option == "Show NSFW Content":
                options_line = "│    "
                for value in self.boolean_options:
                    if value == self.settings["show_nsfw"]:
                        options_line += self.terminal.bright_green(f"[{value}] ")
                    else:
                        options_line += self.terminal.white(f"{value} ")
                output.append(f"{options_line}".ljust(width+21) + "│")
            
            elif option == "Save Settings":
                output.append(f"│    {self.terminal.cyan('Press Enter to save current settings')}".ljust(width+10) + "│")
                output.append(f"╰{'─' * (width-2)}╯")
            
            #output.append(f"├{'─' * (width-2)}┤")
        
        output.append(f"")
        output.append(f"╭{'─' * (width-2)}╮")
        output.append(f"│{self.terminal.bright_cyan('Instructions:').center(width+9)}│")
        output.append(f"│    {self.terminal.white('• Up/Down Arrow: Navigate options')}".ljust(width+10) + "│")
        output.append(f"│    {self.terminal.white('• Left/Right Arrow: Change values')}".ljust(width+10) + "│")
        output.append(f"│    {self.terminal.white('• Enter: Save settings / Login')}".ljust(width+10) + "│")
        output.append(f"│    {self.terminal.white('• Escape: Return without saving')}".ljust(width+10) + "│")
        output.append(f"╰{'─' * (width-2)}╯")

        if self.message and time.time() - self.message_time < 3:
            message_color = self.terminal.red if self.is_error else self.terminal.green
            output.append(f"╭{'─' * (width-2)}╮")
            output.append(f"│{message_color(self.message).center(width+9)}│")
            output.append(f"╰{'─' * (width-2)}╯")
        
        return "\n".join(output)

    def next_option(self):
        self.selected_option = (self.selected_option + 1) % len(self.options)

    def previous_option(self):
        self.selected_option = (self.selected_option - 1) % len(self.options)

    def next_value(self):
        if self.selected_option == 0:  # Login
            return False
        elif self.selected_option == 1:  # Theme
            current_idx = self.themes.index(self.settings["theme"])
            self.settings["theme"] = self.themes[(current_idx + 1) % len(self.themes)]
        elif self.selected_option == 2:  # Posts Per Page
            current_idx = self.posts_per_page_options.index(self.settings["posts_per_page"])
            self.settings["posts_per_page"] = self.posts_per_page_options[(current_idx + 1) % len(self.posts_per_page_options)]
        elif self.selected_option == 3:  # Comment Depth
            current_idx = self.comment_depth_options.index(self.settings["comment_depth"])
            self.settings["comment_depth"] = self.comment_depth_options[(current_idx + 1) % len(self.comment_depth_options)]
        elif self.selected_option == 4:  # Auto Load Comments
            current_idx = self.boolean_options.index(self.settings["auto_load_comments"])
            self.settings["auto_load_comments"] = self.boolean_options[(current_idx + 1) % len(self.boolean_options)]
        elif self.selected_option == 5:  # Show NSFW Content
            current_idx = self.boolean_options.index(self.settings["show_nsfw"])
            self.settings["show_nsfw"] = self.boolean_options[(current_idx + 1) % len(self.boolean_options)]
        elif self.selected_option == 6:  # Save Settings
            if self.save_settings():
                return True
        return False

    def handle_enter(self):
        if self.selected_option == 0:  # Login
            print(self.terminal.clear())
            self.login_screen.display()
            if self.login_screen.reddit_instance:
                self.reddit_instance = self.login_screen.reddit_instance
                self.show_message(f"Successfully logged in as {self.reddit_instance.user.me().name}")
            else:
                self.reddit_instance = None
                self.show_message("Login failed", True)
            return False
        elif self.selected_option == 6:  # Save Settings
            if self.save_settings():
                return True
        return False 