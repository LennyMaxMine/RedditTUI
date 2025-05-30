from blessed import Terminal
import datetime
import time
from services.theme_service import ThemeService
from services.settings_service import Settings

class UserProfileScreen:
    def __init__(self, terminal, reddit_instance):
        self.terminal = terminal
        self.reddit_instance = reddit_instance
        self.theme_service = ThemeService()
        self.user = None
        self.selected_index = 0
        self.scroll_offset = 0
        self.visible_posts = 10
        self.current_tab = "posts"  # posts, comments, or about
        self.tabs = ["posts", "comments", "about"]
        self.tab_index = 0
        self.posts = []
        self.comments = []
        self.is_loading = False
        self.loading_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.loading_index = 0
        self.last_loading_update = 0
        self.width = self.terminal.width - 22
        self.comment_mode = False
        self.comment_text = ""
        self.comment_cursor_pos = 0
        self.settings = Settings()
        self.settings.load_settings_from_file()

    def display(self):
        width = self.terminal.width - 22
        output = []
        
        if self.comment_mode:
            output.append(f"┬{'─' * (width-2)}┤")
            output.append(f"│{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('Add Comment').center(width+21)}│")
            output.append(f"├{'─' * (width-2)}┤")
            output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(self.comment_text[:self.comment_cursor_pos])}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('highlight')))('|')}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(self.comment_text[self.comment_cursor_pos:])}{' ' * (width - len(self.comment_text) - 2)}│")
            output.append(f"├{'─' * (width-2)}┤")
            output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('info')))('Instructions:')}{' ' * (width - 16)}│")
            output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• Type your comment')}{' ' * (width - 20)}│")
            output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• Enter to submit')}{' ' * (width - 20)}│")
            output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• Esc to cancel')}{' ' * (width - 18)}│")
            output.append(f"╰{'─' * (width-2)}╯")
            return "\n".join(output)
        
        output.append(f"┬{'─' * (width-2)}┤")
        output.append(f"│{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('User Profile').center(width+21)}│")
        output.append(f"├{'─' * (width-2)}┤")
        
        if self.user:
            output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('Username: ')}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(f'u/{self.user.name}')}{' ' * (width - len(self.user.name) - 15)}│")
            
            if hasattr(self.user, 'created_utc'):
                created = datetime.datetime.fromtimestamp(self.user.created_utc)
                now = datetime.datetime.now()
                age = now - created
                years = age.days // 365
                months = (age.days % 365) // 30
                days = age.days % 30
                
                output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('Created: ')}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(created.strftime('%Y-%m-%d'))}{' ' * (width - 22)}│")
                output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('Account Age: ')}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(f'{years}y {months}m {days}d')}{' ' * (width - 24)}│")
                
                cake_day = datetime.datetime(now.year, created.month, created.day)
                if cake_day.date() == now.date():
                    output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('🎂 Cake Day: ')}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('success')))('Today!')}{' ' * (width - 20)}│")
                else:
                    output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('🎂 Cake Day: ')}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(cake_day.strftime('%B %d'))}{' ' * (width - 26)}│")
            
            if hasattr(self.user, 'link_karma') and hasattr(self.user, 'comment_karma'):
                output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('Post Karma: ')}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(f'{self.user.link_karma:,}')}{' ' * (width - 16)}│")
                output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('Comment Karma: ')}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(f'{self.user.comment_karma:,}')}{' ' * (width - 20)}│")
                output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('Total Karma: ')}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(f'{self.user.total_karma:,}')}{' ' * (width - 17)}│")
            
            if hasattr(self.user, 'is_gold'):
                output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('Premium: ')}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('highlight')))('Yes') if self.user.is_gold else self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('No')}{' ' * (width - 14)}│")
            
            if hasattr(self.user, 'is_mod'):
                output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('Moderator: ')}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('highlight')))('Yes') if self.user.is_mod else self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('No')}{' ' * (width - 16)}│")
            
            output.append(f"├{'─' * (width-2)}┤")
            
            content_line = self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('subreddit')))("Content: ")
            for i, ctype in enumerate(self.tabs):
                if i == self.tab_index:
                    content_line += self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('highlight')))(f"[{ctype}] ")
                else:
                    content_line += self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(f"{ctype} ")
            output.append(f"│{content_line}{' ' * (width - len(content_line) + 67)}│")
            
            output.append(f"├{'─' * (width-2)}┤")
            
            items = self.posts if self.current_tab == "posts" else self.comments
            if items:
                start_idx = self.scroll_offset
                end_idx = min(start_idx + self.visible_posts, len(items))
                
                for idx, item in enumerate(items[start_idx:end_idx], start=start_idx + 1):
                    if idx - 1 == self.selected_index:
                        prefix = self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('highlight')))("► ")
                    else:
                        prefix = "  "
                    
                    item_num = f"{idx}."
                    if self.current_tab == "posts":  # Posts
                        title = item.title
                        if len(title) > width - 40:
                            title = title[:width-43] + "..."
                        subreddit = self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('subreddit')))(f"r/{item.subreddit.display_name}")
                        score = self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('score')))(f"↑{item.score}")
                        comments = self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('comments')))(f"💬{item.num_comments}")
                        
                        item_line = f"{prefix}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('title')))(item_num)} {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(title)}"
                        metadata = f" | {subreddit} | {score} | {comments}"
                        
                        if hasattr(item, 'over_18') and item.over_18:
                            metadata += f" | {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('error')))('NSFW')}"
                        
                        if hasattr(item, 'stickied') and item.stickied:
                            metadata += f" | {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('warning')))('📌')}"
                        
                        full_line = item_line + metadata
                        if len(full_line) > width - 4:
                            available_space = width - 4 - len(metadata)
                            item_line = f"{prefix}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('title')))(item_num)} {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(title[:available_space-3])}..."
                            full_line = item_line + metadata
                    else:  # Commentstype
                        body = item.body
                        if len(body) > width - 40:
                            body = body[:width-43] + "..."
                        subreddit = self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('subreddit')))(f"r/{item.subreddit.display_name}")
                        score = self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('score')))(f"↑{item.score}")
                        
                        item_line = f"{prefix}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('title')))(item_num)} {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(body)}"
                        metadata = f" | {subreddit} | {score}"
                        
                        full_line = item_line + metadata
                        if len(full_line) > width - 4:
                            available_space = width - 4 - len(metadata)
                            item_line = f"{prefix}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('title')))(item_num)} {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(body[:available_space-3])}..."
                            full_line = item_line + metadata

                    if prefix == "  ":
                        output.append(f"│ {full_line}{' ' * (width - len(full_line) + 109)}│")
                    else:
                        output.append(f"│ {full_line}{' ' * (width - len(full_line) + 132)}│")
                    if idx < end_idx:
                        output.append(f"├{'─' * (width-2)}┤")
            else:
                if self.is_loading:
                    output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('warning')))('Loading content...')}{' ' * (width - 17)}│")
                else:
                    output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('warning')))('No content found.')}{' ' * (width - 20)}│")
        else:
            if self.is_loading:
                output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('warning')))('Loading user profile...')}{' ' * (width - 22)}│")
            else:
                output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('warning')))('No user profile loaded.')}{' ' * (width - 22)}│")
        
        output.append(f"├{'─' * (width-2)}┤")
        output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('info')))('Instructions:')}{' ' * (width - 16)}│")
        output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• Left/Right to switch content type')}{' ' * (width - 38)}│")
        output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• Up/Down to navigate')}{' ' * (width - 24)}│")
        output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• Enter to select item')}{' ' * (width - 25)}│")
        output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• Esc to return to main screen')}{' ' * (width - 33)}│")
        output.append(f"╰{'─' * (width-2)}╯")
        
        if self.is_loading:
            current_time = time.time()
            if current_time - self.last_loading_update >= 0.1:  # Update every 100ms
                self.loading_index = (self.loading_index + 1) % len(self.loading_chars)
                self.last_loading_update = current_time
            loading_text = f"{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('info')))(self.loading_chars[self.loading_index])} Loading..."
            print(self.terminal.move(self.terminal.height - 1, 0) + loading_text)
        
        return "\n".join(output)

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def load_user(self, username):
        if not self.reddit_instance:
            return
        
        self.is_loading = True
        try:
            self.user = self.reddit_instance.redditor(username)
            self.load_user_content()
        except Exception as e:
            print(self.terminal.move(self.terminal.height - 3, 0) + self.terminal.red(f"Error loading user: {e}"))
            self.user = None
            self.posts = []
            self.comments = []
        finally:
            self.is_loading = False

    def load_user_content(self):
        if not self.user:
            return
        
        self.is_loading = True
        try:
            if self.current_tab == "posts":
                self.posts = list(self.user.submissions.new(limit=self.settings.posts_per_page))
                if not self.settings.show_nsfw:
                    self.posts = [post for post in self.posts if not post.over_18]
            elif self.current_tab == "comments":
                self.comments = list(self.user.comments.new(limit=self.settings.posts_per_page))
            self.selected_index = 0
            self.scroll_offset = 0
        except Exception as e:
            self.terminal.print_at(0, 0, f"Error loading content: {str(e)}", self.theme_service.get_color("error"))
        finally:
            self.is_loading = False

    def scroll_up(self):
        items = self.posts if self.current_tab == "posts" else self.comments
        if self.scroll_offset > 0:
            self.scroll_offset = max(0, self.scroll_offset - 3)

    def scroll_down(self):
        items = self.posts if self.current_tab == "posts" else self.comments
        if self.scroll_offset < len(items) - self.visible_posts:
            self.scroll_offset = min(len(items) - self.visible_posts, self.scroll_offset + 3)

    def switch_content_type(self):
        self.tab_index = (self.tab_index + 1) % len(self.tabs)
        self.scroll_offset = 0
        self.selected_index = 0

    def select_item(self):
        if self.current_tab == "posts":
            selected_item = self.posts[self.scroll_offset + self.selected_index]
            return selected_item
        else:  # Comments
            selected_item = self.comments[self.scroll_offset + self.selected_index]
            return selected_item.submission  # Return the parent submission for comments

    def handle_input(self, key):
        if self.comment_mode:
            if key == 'KEY_ENTER':
                self.submit_comment()
                return True
            elif key == 'KEY_ESCAPE':
                self.comment_mode = False
                self.comment_text = ""
                self.comment_cursor_pos = 0
                return True
            elif key == 'KEY_BACKSPACE':
                if self.comment_cursor_pos > 0:
                    self.comment_text = self.comment_text[:self.comment_cursor_pos-1] + self.comment_text[self.comment_cursor_pos:]
                    self.comment_cursor_pos -= 1
            elif key == 'KEY_LEFT':
                if self.comment_cursor_pos > 0:
                    self.comment_cursor_pos -= 1
            elif key == 'KEY_RIGHT':
                if self.comment_cursor_pos < len(self.comment_text):
                    self.comment_cursor_pos += 1
            elif len(key) == 1 and ord(key) >= 32:
                self.comment_text = self.comment_text[:self.comment_cursor_pos] + key + self.comment_text[self.comment_cursor_pos:]
                self.comment_cursor_pos += 1
            return True

        if key == 'KEY_UP':
            if self.selected_index > 0:
                self.selected_index -= 1
            elif self.scroll_offset > 0:
                self.scroll_up()
        elif key == 'KEY_DOWN':
            items = self.posts if self.current_tab == "posts" else self.comments
            if self.selected_index < min(self.visible_posts - 1, len(items) - self.scroll_offset - 1):
                self.selected_index += 1
            elif self.scroll_offset < len(items) - self.visible_posts:
                self.scroll_down()
        elif key == 'KEY_LEFT':
            self.switch_content_type()
            self.load_user_content()
        elif key == 'KEY_RIGHT':
            self.switch_content_type()
            self.load_user_content()
        elif key == 'KEY_ENTER':
            if self.current_tab == "posts" and self.posts:  # Only allow comments on posts
                self.comment_mode = True
                return True
        return key != 'KEY_ESCAPE'

    def submit_comment(self):
        if not self.comment_text.strip():
            return

        try:
            selected_item = self.select_item()
            if selected_item:
                selected_item.reply(self.comment_text)
                self.comment_mode = False
                self.comment_text = ""
                self.comment_cursor_pos = 0
                self.load_user_content()  # Refresh content to show new comment
        except Exception as e:
            print(self.terminal.move(self.terminal.height - 3, 0) + self.terminal.red(f"Error submitting comment: {e}")) 