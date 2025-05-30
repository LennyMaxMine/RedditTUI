from blessed import Terminal
import textwrap
from datetime import datetime
import emoji
from services.settings_service import Settings

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
        self.active = False

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
        age = datetime.utcnow().timestamp() - created_utc
        if age < 3600:  # Less than 1 hour
            return self.terminal.bright_red
        elif age < 86400:  # Less than 1 day
            return self.terminal.red
        elif age < 604800:  # Less than 1 week
            return self.terminal.yellow
        else:
            return self.terminal.normal

    def display(self):
        if not self.posts:
            return "No posts available"
        
        width = self.terminal.width - 24
        output = []
        
        output.append(f"┬{'─' * (width-2)}┬")
        scroll_indicator = f"[{self.selected_index + 1}/{len(self.posts)}]"
        title = f"{self.terminal.bright_blue('Reddit Posts')} {self.terminal.bright_cyan(scroll_indicator)}"
        output.append(f"│{title.center(width+20)}│")
        output.append(f"├{'─' * (width-2)}┤")
        
        posts_per_screen = (self.terminal.height - 6) // 4
        self.visible_posts = max(5, posts_per_screen)
        
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.visible_posts, len(self.posts))

        def contains_emoji(text):
            emojis = emoji.emoji_list(text)
            return int(len(emojis))
        
        for idx, post in enumerate(self.posts[start_idx:end_idx], start=start_idx + 1):
            metadata_additional_width = 53
            if self.current_page in ['top', 'new']:
                metadata_additional_width += 1
            

            if idx - 1 == self.selected_index and self.active:
                prefix = self.terminal.bright_green("│ ► ")
            else:
                prefix = "│   "
            
            title = post.title
            if len(title) > width - 5:
                title = title[:width-8] + "..."
            output.append(f"{prefix}{self.terminal.bold_white(title.ljust(width-5-contains_emoji(title)))}│")
            
            metadata = []
            metadata.append(self.terminal.bright_cyan(f"r/{post.subreddit.display_name}"))
            if post.subreddit.display_name == "explore":
                metadata_additional_width += 2
            metadata.append(self.terminal.bright_yellow(f"u/{post.author}"))
            if hasattr(post, 'url') and any(post.url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                metadata.append(self.terminal.bright_blue("🖼️"))
                metadata_additional_width += 11
            
            score_color = self.get_score_color(post.score)
            metadata.append(f"{score_color}↑{post.score}{self.terminal.normal}")
            metadata.append(self.terminal.bright_magenta(f"💬{post.num_comments}"))
            
            if hasattr(post, 'created_utc'):
                age_color = self.get_age_color(post.created_utc)
                age = datetime.utcnow().timestamp() - post.created_utc
                if age < 3600:
                    age_str = f"{int(age/60)}m"
                elif age < 86400:
                    age_str = f"{int(age/3600)}h"
                else:
                    age_str = f"{int(age/86400)}d"
                metadata.append(f"{age_color}{age_str.replace("-", "")}{self.terminal.normal}")
                
                #Coded all this just to be useless 10min debugging haha (im a dumb shit bruv)
                age_int = ''.join(filter(str.isdigit, age_str))
                if abs(int(age_int)) > 9:
                    metadata_additional_width += 0
                if "-" in age_str:
                    metadata_additional_width -= 0
                #all this above

            
                
            if hasattr(post, 'over_18') and post.over_18:
                metadata.append(self.terminal.bright_red("NSFW"))
                metadata_additional_width += 11
            if hasattr(post, 'stickied') and post.stickied:
                metadata.append(self.terminal.bright_yellow("📌"))
                metadata_additional_width += 11
            
            metadata_line = "│    " + " | ".join(metadata)
            output.append(f"{metadata_line.ljust(width+metadata_additional_width)}│")
            
            if hasattr(post, 'selftext') and post.selftext:
                try:
                    desc = post.selftext.replace('\n', ' ').strip()
                    desc = ''.join(char for char in desc if ord(char) >= 32 or char == '\n')
                    wrapped_desc = textwrap.wrap(desc, width=width-6)
                    if wrapped_desc:
                        first_line = wrapped_desc[0]
                        if len(first_line) > width - 6:
                            first_line = first_line[:width-9] + "..."
                        #output.append(f"│    {self.terminal.normal}{first_line.ljust(width+6)}│")
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
        if not self.settings.show_nsfw:
            new_posts = [post for post in new_posts if not post.over_18]
        self.posts.extend(new_posts)

    def update_posts(self, new_posts):
        if not self.settings.show_nsfw:
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