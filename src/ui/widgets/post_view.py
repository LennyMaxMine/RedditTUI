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
from datetime import datetime
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
from services.theme_service import ThemeService

#AI helped in this thingy (claude)
class PostView:
    def __init__(self, terminal):
        self.terminal = terminal
        self.current_post = None
        self.comments = []
        self.content_width = max(35, self.terminal.width - 24)
        self.comment_scroll_offset = 0
        self.comment_lines = []
        self.need_more_comments = False
        self.from_search = False
        self.vote_status = 0
        self.scroll_position = 0
        self.settings = Settings()
        self.settings.load_settings_from_file()
        self.theme_service = ThemeService()
        self.theme_service.set_theme(self.settings.get_setting('theme'))
        self.comment_mode = False
        self.comment_text = ""
        self.comment_cursor_pos = 0
        self.comment_sort_mode = "best"
        self.comment_sort_index = 0
        self.comment_sort_options = ["best", "top", "new", "controversial"]
        self.report_reasons = [
            "Spam",
            "Vote Manipulation",
            "Personal Information",
            "Sexualizing Minors",
            "Breaking Reddit",
            "Other"
        ]

    def return_current_post(self):
        return self.current_post()
    
    def get_score_color(self, score):
        if score > 1000:
            return self.terminal.bright_green
        elif score > 500:
            return self.terminal.green
        elif score > 100:
            return self.terminal.yellow
        else:
            return self.terminal.normal

    def get_age_color(self, created_utc):
        if not created_utc:
            return self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))
            
        age = max(0, datetime.utcnow().timestamp() - created_utc)
        if age < 3600:
            return self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('warning')))
        elif age < 86400:
            return self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('warning')))
        elif age < 604800:
            return self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('warning')))
        else:
            return self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))

    def get_comment_line_type(self, line):
        if line.startswith("u/") and "|" in line and "points" in line:
            return "header"
        elif line.strip().startswith("─"):
            return "separator"
        else:
            return "content"
        
    def contains_emoji(self, text):
        emojis = emoji.emoji_list(text)
        return int(len(emojis))

    def remove_ansi_escape_sequences(self, text):
        ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', text)
    
    def remove_all_letters(self, text):
        only_numbers_int = re.findall(r'\d+', text)
        return only_numbers_int

    def get_visible_length(self, text):
        clean_text = self.remove_ansi_escape_sequences(text)
        return len(clean_text)

    def display_comment(self, comment, depth=0, width=0):
        if depth > self.settings.get_setting('comment_depth'):
            return []
        output = []
        indent = "  " * depth
        available_width = width - len(indent) - 4
        
        if hasattr(comment, 'body'):
            author = getattr(comment, 'author', '[deleted]')
            score = getattr(comment, 'score', 0)
            created = getattr(comment, 'created_utc', None)
            created_str = ""
            if created:
                dt = datetime.fromtimestamp(created)
                age = datetime.utcnow().timestamp() - created
                if age < 3600:
                    age_str = f"{int(age/60)}m"
                elif age < 86400:
                    age_str = f"{int(age/3600)}h"
                else:
                    age_str = f"{int(age/86400)}d"
                age_color = self.get_age_color(created)
                created_str = f" | {age_color}{age_str.replace('-', '')}{self.terminal.normal}"
            
            score_color = self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))
            author_color = self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('author')))
            
            header_text = f"u/{author} | {score} points{created_str}"
            header_clean = self.remove_ansi_escape_sequences(header_text)
            padding_needed = max(0, available_width - len(header_clean) + 3)
            
            comment_header = f"{indent}{author_color}u/{author}{self.terminal.normal} | {score_color}{score} points{self.terminal.normal}{created_str}{' ' * padding_needed}"
            output.append(comment_header)
            
            comment_body = textwrap.fill(comment.body, width=available_width-2)
            content_color = self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))
            for line in comment_body.splitlines():
                line_padding = max(0, available_width - len(line) - 2)
                output.append(f"{indent}  {content_color}{line}{self.terminal.normal}{' ' * line_padding}")
            
            separator_width = available_width - 2
            separator_color = self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('info')))
            separator_line = "─" * separator_width
            separator_padding = max(0, available_width - separator_width - 2)
            output.append(f"{indent}  {separator_color}{separator_line}{self.terminal.normal}{' ' * separator_padding}")
            
            if hasattr(comment, 'replies') and comment.replies and self.settings.get_setting('auto_load_comments'):
                for reply in comment.replies:
                    if hasattr(reply, 'body'):
                        output.extend(self.display_comment(reply, depth + 1, width))
        
        return output

    def scroll_comments_up(self):
        if self.comment_scroll_offset > 0:
            self.comment_scroll_offset -= 1

    def scroll_comments_down(self):
        if self.comment_scroll_offset < len(self.comment_lines) - self.terminal.height + 10:
            self.comment_scroll_offset += 1
            if self.comment_scroll_offset >= len(self.comment_lines) - self.terminal.height + 15:
                self.need_more_comments = True
            return True
        return False

    def append_comments(self, new_comments):
        self.comments.extend(new_comments)
        self.comment_lines = []
        for comment in self.comments:
            if hasattr(comment, 'body'):
                self.comment_lines.extend(self.display_comment(comment, 0, self.content_width))
        self.need_more_comments = False

    def upvote_post(self):
        if not self.current_post:
            return
        try:
            if self.vote_status == 1:
                self.current_post.clear_vote()
                self.vote_status = 0
                self.current_post.score -= 1
            else:
                if self.vote_status == -1:
                    self.current_post.score += 2
                else:
                    self.current_post.score += 1
                self.current_post.upvote()
                self.vote_status = 1
            self.display_post(self.current_post, self.comments)
        except Exception as e:
            pass

    def downvote_post(self):
        if not self.current_post:
            return
        try:
            if self.vote_status == -1:
                self.current_post.clear_vote()
                self.vote_status = 0
                self.current_post.score += 1
            else:
                if self.vote_status == 1:
                    self.current_post.score -= 2
                else:
                    self.current_post.score -= 1
                self.current_post.downvote()
                self.vote_status = -1
            self.display_post(self.current_post, self.comments)
        except Exception as e:
            pass

    def _hex_to_rgb(self, hex_color):
        if not hex_color or not isinstance(hex_color, str):
            rgb = (255, 255, 255)
            return rgb
        
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join(c*2 for c in hex_color)
        
        try:
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            return rgb
        except ValueError:
            rgb = (255, 255, 255)
            return rgb

    def display_post(self, post, comments=None):
        self.current_post = post
        self.comments = comments or []
        self.comment_lines = []
        self.comment_scroll_offset = 0
        self.comment_mode = False
        self.comment_text = ""
        self.comment_cursor_pos = 0
        self.comment_sort_mode = "best"
        self.comment_sort_index = 0
        self.comment_sort_options = ["best", "top", "new", "controversial"]
        self.from_search = False

        # Process comments
        for comment in self.comments:
            if hasattr(comment, 'body'):
                self.comment_lines.extend(self.display_comment(comment, 0, self.content_width))

    def display(self):
        if not self.current_post:
            return "No post selected"

        width = self.terminal.width - 24
        output = []
        
        # Post title and metadata
        title = self.current_post.title
        if len(title) > width - 4:
            title = title[:width-7] + "..."
        
        output.append(f"┬{'─' * (width-2)}┬")
        output.append(f"│{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('title')))(title.center(width-2))}│")
        output.append(f"├{'─' * (width-2)}┤")
        
        # Post metadata
        metadata = []
        metadata.append(self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('subreddit')))(f"r/{self.current_post.subreddit.display_name}"))
        metadata.append(self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('author')))(f"u/{self.current_post.author}"))
        
        score_color = self.get_score_color(self.current_post.score)
        metadata.append(score_color(f"↑{self.current_post.score}"))
        metadata.append(self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('comments')))(f"💬{self.current_post.num_comments}"))
        
        if hasattr(self.current_post, 'created_utc'):
            age_color = self.get_age_color(self.current_post.created_utc)
            age = datetime.utcnow().timestamp() - self.current_post.created_utc
            if age < 3600:
                age_str = f"{int(age/60)}m"
            elif age < 86400:
                age_str = f"{int(age/3600)}h"
            else:
                age_str = f"{int(age/86400)}d"
            metadata.append(age_color(age_str.replace('-', '')))

        metadata_additional_width = 95
        
        if hasattr(self.current_post, 'over_18') and self.current_post.over_18:
            metadata.append(self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('error')))("NSFW"))
            metadata_additional_width += 2
        if hasattr(self.current_post, 'stickied') and self.current_post.stickied:
            metadata.append(self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('warning')))("📌"))
            metadata_additional_width += 2
        
        metadata_line = "│ " + " | ".join(metadata)
        output.append(f"{metadata_line}{' ' * (width - len(metadata_line) + 2 + metadata_additional_width)}│")
        output.append(f"├{'─' * (width-2)}┤")
        
        if hasattr(self.current_post, 'selftext') and self.current_post.selftext:
            output.append(f"│ {self.terminal.bold_white('Content:').ljust(width+11)} │")
            content = textwrap.fill(self.current_post.selftext, width=width-4)
            for line in content.splitlines():
                output.append(f"│ {line.ljust(width-4)} │")
        elif hasattr(self.current_post, 'url'):
            output.append(f"│ {self.terminal.bold_white('Link Post:').ljust(width+11)} │")
            output.append(f"│ {self.terminal.bright_cyan(f'URL: {self.current_post.url}').ljust(width+7)} │")
            if hasattr(self.current_post, 'preview') and self.current_post.preview:
                output.append(f"│ {self.terminal.bright_yellow('Preview available (not shown)').ljust(width+7)} │")
            
            image_links = self.get_image_links(self.current_post)
            if image_links:
                output.append(f"│ {self.terminal.bold_white('Image Links:').ljust(width+11)} │")
                for link in image_links:
                    output.append(f"│ {self.terminal.bright_cyan(link).ljust(width+7)} │")
        
        if self.comments:
            output.append(f"├{'─' * (width-2)}┤")
            output.append(f"│ {self.terminal.bold_white('Comments:').ljust(width+11)} │")
            output.append(f"├{'─' * (width-2)}┤")
            
            sort_options_line = "│ Sort: "
            for i, option in enumerate(self.comment_sort_options):
                if i == self.comment_sort_index:
                    sort_options_line += self.terminal.bright_green(f"[{option}] ")
                else:
                    sort_options_line += self.terminal.white(f"{option} ")
            sort_options_line = sort_options_line.ljust(width + 43) + "│"
            output.append(sort_options_line)
            output.append(f"├{'─' * (width-2)}┤")
            
            self.comment_lines = []
            for comment in self.comments:
                if hasattr(comment, 'body'):
                    self.comment_lines.extend(self.display_comment(comment, 0, width))
            
            if len(self.comment_lines) > self.terminal.height - 10:
                scroll_info = f"Scroll: {self.comment_scroll_offset + 1}-{min(self.comment_scroll_offset + self.terminal.height - 10, len(self.comment_lines))} of {len(self.comment_lines)}"
                output.append(f"│ {self.terminal.bright_blue(scroll_info.center(width-4))} │")
                output.append(f"├{'─' * (width-2)}┤")
            
            visible_lines = self.comment_lines[self.comment_scroll_offset:self.comment_scroll_offset + self.terminal.height - 10]
            for line in visible_lines:
                clean_line = self.remove_ansi_escape_sequences(line)
                emoji_count = self.contains_emoji(clean_line) *2
                padding_needed = max(0, width - 2 - len(clean_line) - emoji_count)
                output.append(f"│ {line}{' ' * padding_needed} │")
        
        output.append(f"╰{'─' * (width-2)}╯")
        return "\n".join(output)

    def update_post(self, post, reddit_instance):
        self.current_post = post
        self.reddit_instance = reddit_instance
        if hasattr(post, 'comments'):
            post.comments.replace_more(limit=0)
            self.comments = list(post.comments.list())
        else:
            self.comments = []

    def report_post(self):
        if not self.reddit_instance:
            self.terminal.move(self.terminal.height - 3, 0)
            print(self.terminal.red("You must be logged in to report posts"))
            return True

        width = self.content_width
        output = []
        
        output.append(f"┬{'─' * (width-2)}┬")
        output.append(f"│{self.terminal.bold_white('Report Post').center(width+13)}│")
        output.append(f"├{'─' * (width-2)}┤")
        
        for idx, reason in enumerate(self.report_reasons, 1):
            output.append(f"│ {self.terminal.bright_cyan(f'{idx}.')} {reason.ljust(width+5)} │")
        
        output.append(f"├{'─' * (width-2)}┤")
        output.append(f"│ {self.terminal.bright_yellow('Enter number (1-6) or press ESC to cancel').ljust(width+5)} │")
        output.append(f"╰{'─' * (width-2)}╯")
        
        self.terminal.move(0, 0)
        print("\n".join(output))
        
        try:
            choice = int(Prompt.ask("\nEnter number", default="6"))
            if 1 <= choice <= len(self.report_reasons):
                reason = self.report_reasons[choice - 1]
                if reason == "Other":
                    output = []
                    output.append(f"┬{'─' * (width-2)}┬")
                    output.append(f"│{self.terminal.bold_white('Specify Reason').center(width+13)}│")
                    output.append(f"├{'─' * (width-2)}┤")
                    output.append(f"│ {self.terminal.bright_yellow('Enter your reason:').ljust(width+5)} │")
                    output.append(f"╰{'─' * (width-2)}╯")
                    self.terminal.move(0, 0)
                    print("\n".join(output))
                    reason = Prompt.ask("Reason")
                
                self.reddit_instance.submission(self.current_post.id).report(reason)
                output = []
                output.append(f"┬{'─' * (width-2)}┬")
                output.append(f"│{self.terminal.bold_green('Post reported successfully').center(width+13)}│")
                output.append(f"╰{'─' * (width-2)}╯")
                self.terminal.move(0, 0)
                print("\n".join(output))
            else:
                output = []
                output.append(f"┬{'─' * (width-2)}┬")
                output.append(f"│{self.terminal.bold_red('Invalid choice').center(width+13)}│")
                output.append(f"╰{'─' * (width-2)}╯")
                self.terminal.move(0, 0)
                print("\n".join(output))
        except ValueError:
            output = []
            output.append(f"┬{'─' * (width-2)}┬")
            output.append(f"│{self.terminal.bold_red('Invalid input').center(width+13)}│")
            output.append(f"╰{'─' * (width-2)}╯")
            self.terminal.move(0, 0)
            print("\n".join(output))
        except Exception as e:
            output = []
            output.append(f"┬{'─' * (width-2)}┬")
            output.append(f"│{self.terminal.bold_red(f'Error reporting post: {str(e)}').center(width+13)}│")
            output.append(f"╰{'─' * (width-2)}╯")
            self.terminal.move(0, 0)
            print("\n".join(output))
        return True

    def get_image_links(self, post):
        links = []
        if hasattr(post, 'url'):
            if post.url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.gifv')):
                links.append(post.url)
            elif 'imgur.com' in post.url:
                links.append(post.url)
            elif 'reddit.com/gallery' in post.url:
                if hasattr(post, 'gallery_data'):
                    for item in post.gallery_data['items']:
                        media_id = item['media_id']
                        if media_id in post.media_metadata:
                            if 'p' in post.media_metadata[media_id]:
                                links.append(post.media_metadata[media_id]['p'][0]['u'])
        if hasattr(post, 'media_metadata'):
            for media_id, metadata in post.media_metadata.items():
                if 'p' in metadata:
                    links.append(metadata['p'][0]['u'])
        return links

    def submit_comment(self):
        if not self.comment_text.strip():
            return

        try:
            self.current_post.reply(self.comment_text)
            self.comment_mode = False
            self.comment_text = ""
            self.comment_cursor_pos = 0
            if hasattr(self.current_post, 'comments'):
                self.current_post.comments.replace_more(limit=0)
                self.comments = list(self.current_post.comments.list())
                self.comment_lines = []
                for comment in self.comments:
                    if hasattr(comment, 'body'):
                        self.comment_lines.extend(self.display_comment(comment, 0, self.content_width))
        except Exception as e:
            print(self.terminal.move(self.terminal.height - 3, 0) + self.terminal.red(f"Error submitting comment: {e}"))