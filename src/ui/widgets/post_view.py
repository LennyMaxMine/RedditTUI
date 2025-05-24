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
            return self.terminal.normal
            
        age = max(0, datetime.datetime.utcnow().timestamp() - created_utc)
        if age < 3600:
            return self.terminal.bright_red
        elif age < 86400:
            return self.terminal.red
        elif age < 604800:
            return self.terminal.yellow
        else:
            return self.terminal.normal

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

    def display_comment(self, comment, depth=0, width=0):
        output = []
        indent = "  " * depth
        
        if hasattr(comment, 'body'):
            author = getattr(comment, 'author', '[deleted]')
            score = getattr(comment, 'score', 0)
            created = getattr(comment, 'created_utc', None)
            created_str = ""
            if created:
                dt = datetime.datetime.utcfromtimestamp(created)
                age = datetime.datetime.utcnow().timestamp() - created
                if age < 3600:
                    age_str = f"{int(age/60)}m"
                elif age < 86400:
                    age_str = f"{int(age/3600)}h"
                else:
                    age_str = f"{int(age/86400)}d"
                age_color = self.get_age_color(created)
                created_str = f" | {age_color}{age_str.replace("-", "")}{self.terminal.normal}"
            
            score_color = self.get_score_color(score)
            comment_header = f"{indent}{self.terminal.bright_yellow(f'u/{author}')} | {score_color}{score} points{self.terminal.normal}{created_str}:"
            output.append(comment_header)
            
            comment_body = textwrap.fill(comment.body, width=width-6-(depth*2))
            for line in comment_body.splitlines():
                output.append(f"{indent}  {self.terminal.white(line)}")
            
            separator = "─" * (width-6-(depth*2))
            output.append(f"{indent}  {self.terminal.bright_blue(separator)}")
            
            if hasattr(comment, 'replies') and comment.replies:
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

    def display(self):
        if not self.current_post:
            return ""
        width = self.content_width
        output = []
        
        output.append(f"┬{'─' * (width-2)}┬")
        output.append(f"│{self.terminal.bold_white(f'r/{self.current_post.subreddit.display_name}/{self.current_post.title}').center(width+13)}│")
        output.append(f"├{'─' * (width-2)}┤")
        
        metadata = []
        if hasattr(self.current_post, 'origin'):
            origin_exists = True
            #metadata.append(self.terminal.bright_blue(f"From: {self.current_post.origin}"))
            #metadata.append("")
            pass
        else:
            origin_exists = False
            
        metadata.append(self.terminal.bright_cyan(f"Subreddit: r/{self.current_post.subreddit.display_name}"))
        metadata.append(self.terminal.bright_yellow(f"Author: u/{self.current_post.author}"))
        
        score_color = self.get_score_color(self.current_post.score)
        metadata.append(f"{score_color}Score: {self.current_post.score}{self.terminal.normal}")
        metadata.append(self.terminal.bright_magenta(f"Comments: {self.current_post.num_comments}"))
        
        if hasattr(self.current_post, 'created_utc'):
            age_color = self.get_age_color(self.current_post.created_utc)
            age = datetime.datetime.utcnow().timestamp() - self.current_post.created_utc
            if age < 3600:
                age_str = f"{int(age/60)}m ago"
            elif age < 86400:
                age_str = f"{int(age/3600)}h ago"
            else:
                age_str = f"{int(age/86400)}d ago"
            if "-"in age_str: additionalchar = 1
            else: additionalchar = 0
            for i in range(0, len(self.remove_all_letters(age_str))):
                additionalchar += 1
            metadata.append(f"{age_color}Posted: {age_str.replace("-", "")}{self.terminal.normal}")
        
        if hasattr(self.current_post, 'url'):
            if additionalchar >= 1 and origin_exists == True: addchar = " "
            else: addchar = ""
            metadata.append(self.terminal.bright_cyan(f"{addchar}URL: {self.current_post.url}"))
            
        if hasattr(self.current_post, 'is_self'):
            metadata.append(self.terminal.bright_yellow(f"Type: {'Self Post' if self.current_post.is_self else 'Link Post'}"))
            
        if hasattr(self.current_post, 'upvote_ratio'):
            ratio = self.current_post.upvote_ratio
            if ratio > 0.8:
                color = self.terminal.bright_green
            elif ratio > 0.6:
                color = self.terminal.green
            elif ratio > 0.4:
                color = self.terminal.yellow
            else:
                color = self.terminal.red
            metadata.append(f"{color}Upvote Ratio: {ratio:.1%}{self.terminal.normal}")
            
        if hasattr(self.current_post, 'over_18'):
            if self.current_post.over_18:
                metadata.append(self.terminal.bright_red("NSFW: Yes"))
            else:
                metadata.append(self.terminal.bright_green("NSFW: No"))
            
        if hasattr(self.current_post, 'spoiler'):
            if self.current_post.spoiler:
                metadata.append(self.terminal.bright_yellow("Spoiler: Yes"))
            else:
                metadata.append(self.terminal.bright_green("Spoiler: No"))
            
        if hasattr(self.current_post, 'locked'):
            if self.current_post.locked:
                metadata.append(self.terminal.bright_red("Locked: Yes"))
            else:
                metadata.append(self.terminal.bright_green("Locked: No"))
            
        if hasattr(self.current_post, 'stickied'):
            if self.current_post.stickied:
                metadata.append(self.terminal.bright_yellow("Stickied: Yes"))
            else:
                metadata.append(self.terminal.bright_green("Stickied: No"))
        
        metadata_lines = []
        for i in range(0, len(metadata), 2):
            line = metadata[i]
            if i + 1 < len(metadata):
                line = line.ljust(width // 2) + metadata[i + 1]
            if "URL" in line and origin_exists == True:
                metadata_lines.append(f"│ {line.ljust(width+19)} │")
            if "points" in line and origin_exists == True:
                splitline = line.split("|")
                getnum = self.remove_all_letters(splitline[1])
                numcount = 0
                for num in getnum:
                    numcount += int(num)
                if numcount <= 100: 
                    metadata_lines.append(f"│ {line.ljust(width+19)} │")
                else:
                    metadata_lines.append(f"│ {line.ljust(width+18)} │")

            else:
                metadata_lines.append(f"│ {line.ljust(width+18)} │")
        
        output.extend(metadata_lines)
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
        
        if self.comments:
            output.append(f"├{'─' * (width-2)}┤")
            output.append(f"│ {self.terminal.bold_white('Comments:').ljust(width+11)} │")
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
                line_type = self.get_comment_line_type(self.remove_ansi_escape_sequences(line.strip()))
                if line_type == "header":
                    output.append(f"│ {line.ljust(width+30-self.contains_emoji(line))} │")
                else:
                    output.append(f"│ {line.ljust(width+7-self.contains_emoji(line))} │")
        
        output.append(f"╰{'─' * (width-2)}╯")
        return "\n".join(output)

    def display_post(self, post, comments=None):
        self.current_post = post
        self.comments = comments or []