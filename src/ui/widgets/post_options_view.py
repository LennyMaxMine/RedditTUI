from textual.app import App
from textual.scroll_view import ScrollView
from textual.widgets import Static, Header, Footer
from textual.containers import Container, Horizontal
from textual.reactive import Reactive
from textual import events
from blessed import Terminal
import textwrap
import requests
from PIL import Image
from io import BytesIO
import os
import tempfile
import datetime
import emoji
import re
from pyshorteners import Shortener
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich import box
from rich.prompt import Prompt
from services.settings_service import Settings

class PostOptionsScreen:
    def __init__(self, terminal):
        self.terminal = terminal
        self.current_post = None
        self.settings = Settings()
        self.settings.load_settings_from_file()
        self.content_width = max(35, self.terminal.width - 24)
        self.report_reasons = [
            "Spam",
            "Vote Manipulation",
            "Personal Information",
            "Sexualizing Minors",
            "Breaking Reddit",
            "Other"
        ]
        self.reddit_instance = None
        self.confirming_report = False
        self.selected_reason = None
        self.confirming_save = False
        self.status_message = None
        self.status_color = None

    def get_short_url(self, url):
        try:
            s = Shortener()
            return s.tinyurl.short(url)
        except:
            return url

    def handle_input(self, key):
        if self.confirming_save:
            if key.lower() == 'y':
                try:
                    if hasattr(self.current_post, 'saved') and self.current_post.saved:
                        self.current_post.unsave()
                        self.status_message = "Post unsaved successfully"
                        self.status_color = "green"
                        return "unsaved"
                    else:
                        self.current_post.save()
                        self.status_message = "Post saved successfully"
                        self.status_color = "green"
                        return "saved"
                except Exception as e:
                    self.status_message = f"Error: {str(e)}"
                    self.status_color = "red"
                    return f"error:{str(e)}"
            elif key.lower() == 'n':
                self.confirming_save = False
            return None
        elif self.confirming_report:
            if key in ['\r', '\n', '\x0a', '\x0d', '\x1b\x0d', '\x1b\x0a']:  # Enter
                if self.selected_reason:
                    try:
                        if self.selected_reason == "Other":
                            reason = Prompt.ask("Enter your reason")
                        else:
                            reason = self.selected_reason
                        self.reddit_instance.submission(self.current_post.id).report(reason)
                        self.confirming_report = False
                        self.selected_reason = None
                        self.status_message = "Post reported successfully"
                        self.status_color = "green"
                        return "reported"
                    except Exception as e:
                        self.confirming_report = False
                        self.selected_reason = None
                        self.status_message = f"Error: {str(e)}"
                        self.status_color = "red"
                        return f"error:{str(e)}"
            elif key == '\x1b':  # Escape
                self.confirming_report = False
                self.selected_reason = None
                return None
        elif key.isdigit() and 1 <= int(key) <= len(self.report_reasons):
            self.selected_reason = self.report_reasons[int(key) - 1]
            self.confirming_report = True
            return None
        elif key.lower() == 's':
            self.confirming_save = True
            return None
        return None

    def display(self):
        if not self.current_post:
            return ""
        width = self.content_width
        output = []

        post_url = f"https://reddit.com{self.current_post.permalink}"
        short_url = self.get_short_url(post_url)

        output.append(f"┬{'─' * (width-2)}┬")
        output.append(f"│{self.terminal.bold_white(f'r/{self.current_post.subreddit.display_name}/{self.current_post.title}    -    options').center(width+13)}│")
        output.append(f"├{'─' * (width-2)}┤")
        
        output.append(f"│ {self.terminal.bold_cyan('Post Options').center(width+11)} │")
        output.append(f"│{'─' * (width-2)}│")
        
        output.append(f"│ {self.terminal.bold_white('Title: ').ljust(10)}{self.terminal.white(self.current_post.title).ljust(width)} │")
        output.append(f"│ {self.terminal.bold_white('Author: ').ljust(10)}{self.terminal.white(f'u/{self.current_post.author}').ljust(width-1)} │")
        output.append(f"│ {self.terminal.bold_white('URL: ').ljust(10)}{self.terminal.white(short_url).ljust(width+2)} │")
        
        output.append(f"│{'─' * (width-2)}│")
        output.append(f"│ {self.terminal.bold_white('Report Options: ').ljust(width+11)} │")
        for i, reason in enumerate(self.report_reasons, 1):
            if self.confirming_report and reason == self.selected_reason:
                output.append(f"│ {self.terminal.bright_cyan(f'{i}.')} {self.terminal.bright_yellow(reason).ljust(width+4)} │")
            else:
                output.append(f"│ {self.terminal.bright_cyan(f'{i}.')} {self.terminal.white(reason).ljust(width+4)} │")
        
        output.append(f"│{'─' * (width-2)}│")
        output.append(f"│ {self.terminal.bold_white('Other Options: ').ljust(width+11)} │")
        if hasattr(self.current_post, 'saved') and self.current_post.saved:
            output.append(f"│ {self.terminal.bright_cyan('S.')} {self.terminal.white('Unsave Post').ljust(width+4)} │")
        else:
            output.append(f"│ {self.terminal.bright_cyan('S.')} {self.terminal.white('Save Post').ljust(width+4)} │")
        
        if self.status_message:
            output.append(f"│{'─' * (width-2)}│")
            if self.status_color == "green":
                output.append(f"│ {self.terminal.bright_green(self.status_message.center(width+7))} │")
            else:
                output.append(f"│ {self.terminal.bright_red(self.status_message.center(width+7))} │")
            self.status_message = None
            self.status_color = None
        elif self.confirming_save:
            output.append(f"│{'─' * (width-2)}│")
            if hasattr(self.current_post, 'saved') and self.current_post.saved:
                output.append(f"│ {self.terminal.bright_yellow('Are you sure you want to unsave this post? (Y/N)').center(width+7)} │")
            else:
                output.append(f"│ {self.terminal.bright_yellow('Are you sure you want to save this post? (Y/N)').center(width+7)} │")
        elif self.confirming_report:
            output.append(f"│{'─' * (width-2)}│")
            output.append(f"│ {self.terminal.bright_yellow('Press Enter to confirm report or ESC to cancel').center(width+7)} │")
        else:
            output.append(f"│{'─' * (width-2)}│")
            output.append(f"│ {self.terminal.bright_yellow('Press ESC to return').center(width+7)} │")
        output.append(f"╰{'─' * (width-2)}╯")

        return "\n".join(output)