from blessed import Terminal
import textwrap
from datetime import datetime
import emoji
from services.settings_service import Settings
from services.theme_service import ThemeService

class PostList:
    def __init__(self, terminal, visible_posts=10, current_page='home'):
        self.terminal = terminal
        self.posts = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.visible_posts = visible_posts
        self.loading_more = False
        self.current_page = 'home'
        self.settings = Settings()
        self.settings.load_settings_from_file()
        self.theme_service = ThemeService()
        self.active = False

    def get_score_color(self, score):
        if score > 1000:
            return self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('score')))
        elif score > 500:
            return self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('score')))
        elif score > 100:
            return self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('score')))
        else:
            return self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))

    def get_age_color(self, created_utc):
        age = datetime.utcnow().timestamp() - created_utc
        if age < 3600:
            return self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('warning')))
        elif age < 86400:
            return self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('warning')))
        elif age < 604800:
            return self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('warning')))
        else:
            return self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))

    def _get_display_length(self, text):
        """Calculate the actual display length of text, accounting for ANSI codes and emojis"""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_text = ansi_escape.sub('', text)
        emoji_count = len(emoji.emoji_list(clean_text))
        return len(clean_text) - emoji_count

    def display(self):
        if not self.posts:
            return "No posts available"
        
        width = self.terminal.width - 24
        output = []
        
        output.append(f"┬{'─' * (width-2)}┬")
        scroll_indicator = f"[{self.selected_index + 1}/{len(self.posts)}]"
        title = f"{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('Reddit Posts')} {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('info')))(scroll_indicator)}"
        output.append(f"│{title.center(width+44)}│")
        output.append(f"├{'─' * (width-2)}┤")
        
        posts_per_screen = (self.terminal.height - 6) // 4
        self.visible_posts = max(5, posts_per_screen)
        
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.visible_posts, len(self.posts))

        def contains_emoji(text):
            emojis = emoji.emoji_list(text)
            return int(len(emojis))
        
        for idx, post in enumerate(self.posts[start_idx:end_idx], start=start_idx + 1):
            if idx - 1 == self.selected_index and self.active:
                prefix = self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('highlight')))("│ ► ")
            else:
                prefix = "│   "
            
            metadata_additional_width = 12

            title = post.title
            if len(title) > width - 5:
                title = title[:width-8] + "..."
            output.append(f"{prefix}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('title')))(title.ljust(width-5-contains_emoji(title)))}│")
            
            metadata = []
            metadata.append(self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('subreddit')))(f"r/{post.subreddit.display_name}"))
            metadata.append(self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('author')))(f"u/{post.author}"))
            
            if hasattr(post, 'url') and any(post.url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                metadata.append(self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('info')))("🖼️"))
                metadata_additional_width += 2
            
            score_color = self.get_score_color(post.score)
            metadata.append(score_color(f"↑{post.score}"))
            metadata.append(self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('comments')))(f"💬{post.num_comments}"))
            
            if hasattr(post, 'created_utc'):
                age_color = self.get_age_color(post.created_utc)
                age = datetime.utcnow().timestamp() - post.created_utc
                if age < 3600:
                    age_str = f"{int(age/60)}m"
                elif age < 86400:
                    age_str = f"{int(age/3600)}h"
                else:
                    age_str = f"{int(age/86400)}d"
                metadata.append(age_color(age_str.replace('-', '')))
            
            if hasattr(post, 'over_18') and post.over_18:
                metadata.append(self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('error')))("NSFW"))
                metadata_additional_width += 1
            if hasattr(post, 'stickied') and post.stickied:
                metadata.append(self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('warning')))("📌"))
                metadata_additional_width += 1
            
            metadata_line = "│    " + " | ".join(metadata)
            metadata_display_length = self._get_display_length(metadata_line)
            padding_needed = width - metadata_display_length + metadata_additional_width
            output.append(f"{metadata_line}{' ' * padding_needed}│")
            
            if hasattr(post, 'selftext') and post.selftext:
                try:
                    desc = post.selftext.replace('\n', ' ').strip()
                    desc = ''.join(char for char in desc if ord(char) >= 32 or char == '\n')
                    wrapped_desc = textwrap.wrap(desc, width=width-6)
                    if wrapped_desc:
                        first_line = wrapped_desc[0]
                        if len(first_line) > width - 6:
                            first_line = first_line[:width-9] + "..."
                except Exception:
                    pass
            
            if idx < end_idx:
                output.append(f"├{'─' * (width-2)}┤")
            else:
                output.append(f"╰{'─' * (width-2)}╯")
        
        return "\n".join(output)

    def get_selected_post(self):
        if 0 <= self.selected_index < len(self.posts):
            return self.posts[self.selected_index]
        return None

    def append_posts(self, new_posts):
        if not self.settings.get_setting('show_nsfw'):
            new_posts = [post for post in new_posts if not post.over18]
        self.posts.extend(new_posts)

    def update_posts(self, new_posts):
        if not self.settings.get_setting('show_nsfw'):
            new_posts = [post for post in new_posts if not post.over_18]
        self.posts = new_posts
        self.selected_index = 0
        self.scroll_offset = 0

    def scroll_down(self):
        if self.selected_index < len(self.posts) - 1:
            self.selected_index += 1
            if self.selected_index >= self.scroll_offset + self.visible_posts:
                self.scroll_offset = self.selected_index - self.visible_posts + 1
            if self.selected_index >= len(self.posts) - 5 and not self.loading_more:
                self.loading_more = True
                return True
        return False

    def scroll_up(self):
        if self.selected_index > 0:
            self.selected_index -= 1
            if self.selected_index < self.scroll_offset:
                self.scroll_offset = self.selected_index

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def handle_input(self, key):
        if key == '\x1b[A':  # Up Arrow
            self.scroll_up()
            return True
        elif key == '\x1b[B':  # Down Arrow
            return self.scroll_down()
        elif key == '\r' or key == '\n':  # Enter
            return self.get_selected_post()
        return False