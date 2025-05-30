from blessed import Terminal
import datetime
import time

class UserProfileScreen:
    def __init__(self, terminal, reddit_instance):
        self.terminal = terminal
        self.reddit_instance = reddit_instance
        self.user = None
        self.posts = []
        self.comments = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.visible_results = 10
        self.content_types = ["posts", "comments"]
        self.content_index = 0
        self.is_loading = False
        self.loading_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.loading_index = 0
        self.last_loading_update = 0
        self.width = self.terminal.width - 22

    def display(self):
        width = self.terminal.width - 22
        output = []
        
        output.append(f"┬{'─' * (width-2)}┤")
        output.append(f"│{self.terminal.bold_white('User Profile').center(width+13)}│")
        output.append(f"├{'─' * (width-2)}┤")
        
        if self.user:
            output.append(f"│ {self.terminal.bold_white('Username: ')}{self.terminal.white(f'u/{self.user.name}')}{' ' * (width - len(self.user.name) - 15)}│")
            output.append(f"│ {self.terminal.bold_white('Karma: ')}{self.terminal.white(f'{self.user.total_karma:,}')}{' ' * (width - len(str(self.user.total_karma)) - 10)}│")
            if hasattr(self.user, 'created_utc'):
                created = datetime.datetime.fromtimestamp(self.user.created_utc)
                output.append(f"│ {self.terminal.bold_white('Created: ')}{self.terminal.white(created.strftime('%Y-%m-%d'))}{' ' * (width - 22)}│")
            
            output.append(f"├{'─' * (width-2)}┤")
            
            content_line = self.terminal.cyan("Content: ")
            for i, ctype in enumerate(self.content_types):
                if i == self.content_index:
                    content_line += self.terminal.green(f"[{ctype}] ")
                else:
                    content_line += self.terminal.white(f"{ctype} ")
            output.append(f"│{content_line}{' ' * (width - len(content_line) + 31)}│")
            
            output.append(f"├{'─' * (width-2)}┤")
            
            items = self.posts if self.content_index == 0 else self.comments
            if items:
                start_idx = self.scroll_offset
                end_idx = min(start_idx + self.visible_results, len(items))
                
                for idx, item in enumerate(items[start_idx:end_idx], start=start_idx + 1):
                    if idx - 1 == self.selected_index:
                        prefix = self.terminal.green("► ")
                    else:
                        prefix = "  "
                    
                    item_num = f"{idx}."
                    if self.content_index == 0:  # Posts
                        title = item.title
                        if len(title) > width - 40:
                            title = title[:width-43] + "..."
                        subreddit = self.terminal.cyan(f"r/{item.subreddit.display_name}")
                        score = self.terminal.green(f"↑{item.score}")
                        comments = self.terminal.magenta(f"💬{item.num_comments}")
                        
                        item_line = f"{prefix}{self.terminal.bold_white(item_num)} {self.terminal.white(title)}"
                        metadata = f" | {subreddit} | {score} | {comments}"
                        
                        if hasattr(item, 'over_18') and item.over_18:
                            metadata += f" | {self.terminal.red('NSFW')}"
                        
                        if hasattr(item, 'stickied') and item.stickied:
                            metadata += f" | {self.terminal.yellow('📌')}"
                        
                        full_line = item_line + metadata
                        if len(full_line) > width - 4:
                            available_space = width - 4 - len(metadata)
                            item_line = f"{prefix}{self.terminal.bold_white(item_num)} {self.terminal.white(title[:available_space-3])}..."
                            full_line = item_line + metadata
                    else:  # Comments
                        body = item.body
                        if len(body) > width - 40:
                            body = body[:width-43] + "..."
                        subreddit = self.terminal.cyan(f"r/{item.subreddit.display_name}")
                        score = self.terminal.green(f"↑{item.score}")
                        
                        item_line = f"{prefix}{self.terminal.bold_white(item_num)} {self.terminal.white(body)}"
                        metadata = f" | {subreddit} | {score}"
                        
                        full_line = item_line + metadata
                        if len(full_line) > width - 4:
                            available_space = width - 4 - len(metadata)
                            item_line = f"{prefix}{self.terminal.bold_white(item_num)} {self.terminal.white(body[:available_space-3])}..."
                            full_line = item_line + metadata

                    if prefix == "  ":
                        output.append(f"│ {full_line}{' ' * (width - len(full_line) + 55)}│")
                    else:
                        output.append(f"│ {full_line}{' ' * (width - len(full_line) + 66)}│")
                    if idx < end_idx:
                        output.append(f"├{'─' * (width-2)}┤")
            else:
                if self.is_loading:
                    output.append(f"│ {self.terminal.yellow('Loading content...')}{' ' * (width - 17)}│")
                else:
                    output.append(f"│ {self.terminal.yellow('No content found.')}{' ' * (width - 20)}│")
        else:
            if self.is_loading:
                output.append(f"│ {self.terminal.yellow('Loading user profile...')}{' ' * (width - 22)}│")
            else:
                output.append(f"│ {self.terminal.yellow('No user profile loaded.')}{' ' * (width - 22)}│")
        
        output.append(f"├{'─' * (width-2)}┤")
        output.append(f"│ {self.terminal.cyan('Instructions:')}{' ' * (width - 16)}│")
        output.append(f"│ {self.terminal.white('• Left/Right to switch content type')}{' ' * (width - 38)}│")
        output.append(f"│ {self.terminal.white('• Up/Down to navigate')}{' ' * (width - 24)}│")
        output.append(f"│ {self.terminal.white('• Enter to select item')}{' ' * (width - 25)}│")
        output.append(f"│ {self.terminal.white('• Esc to return to main screen')}{' ' * (width - 33)}│")
        output.append(f"╰{'─' * (width-2)}╯")
        
        if self.is_loading:
            current_time = time.time()
            if current_time - self.last_loading_update >= 0.1:  # Update every 100ms
                self.loading_index = (self.loading_index + 1) % len(self.loading_chars)
                self.last_loading_update = current_time
            loading_text = f"{self.terminal.bright_blue(self.loading_chars[self.loading_index])} Loading..."
            print(self.terminal.move(self.terminal.height - 1, 0) + loading_text)
        
        return "\n".join(output)

    def load_user(self, username):
        if not self.reddit_instance:
            return
        
        self.is_loading = True
        try:
            self.user = self.reddit_instance.redditor(username)
            self.load_content()
        except Exception as e:
            print(self.terminal.move(self.terminal.height - 3, 0) + self.terminal.red(f"Error loading user: {e}"))
            self.user = None
            self.posts = []
            self.comments = []
        finally:
            self.is_loading = False

    def load_content(self):
        if not self.user:
            return
        
        self.is_loading = True
        try:
            if self.content_index == 0:  # Posts
                self.posts = list(self.user.submissions.new(limit=25))
            else:  # Comments
                self.comments = list(self.user.comments.new(limit=25))
            self.selected_index = 0
            self.scroll_offset = 0
        except Exception as e:
            print(self.terminal.move(self.terminal.height - 3, 0) + self.terminal.red(f"Error loading content: {e}"))
            if self.content_index == 0:
                self.posts = []
            else:
                self.comments = []
        finally:
            self.is_loading = False

    def scroll_up(self):
        if self.scroll_offset > 0:
            self.scroll_offset = max(0, self.scroll_offset - 3)

    def scroll_down(self):
        if self.scroll_offset < len(self.posts) - self.visible_results:
            self.scroll_offset = min(len(self.posts) - self.visible_results, self.scroll_offset + 3)

    def switch_content_type(self):
        self.content_index = (self.content_index + 1) % len(self.content_types)

    def select_item(self):
        if self.content_index == 0:  # Posts
            selected_item = self.posts[self.scroll_offset + self.selected_index]
            print(f"Selected post: {selected_item.title}")
        else:  # Comments
            selected_item = self.comments[self.scroll_offset + self.selected_index]
            print(f"Selected comment: {selected_item.body}") 