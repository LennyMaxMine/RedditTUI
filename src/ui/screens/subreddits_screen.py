from blessed import Terminal
import textwrap
from services.theme_service import ThemeService
import time

class SubredditsScreen:
    def __init__(self, terminal, reddit_instance):
        self.terminal = terminal
        self.reddit_instance = reddit_instance
        self.theme_service = ThemeService()
        self.selected_index = 0
        self.scroll_offset = 0
        self.visible_subreddits = 10
        self.subreddits = []
        self.post_categories = ["hot", "new", "top", "rising"]
        self.selected_category = 0
        self.is_loading = False
        self.loading_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.loading_index = 0
        self.last_loading_update = 0
        self.load_subreddits()

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def load_subreddits(self):
        if not self.reddit_instance:
            return
        
        self.is_loading = True
        try:
            self.subreddits = list(self.reddit_instance.user.subreddits(limit=100))
            self.selected_index = 0
            self.scroll_offset = 0
        except Exception as e:
            print(self.terminal.move(self.terminal.height - 3, 0) + self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('error')))(f"Error loading subreddits: {e}"))
            self.subreddits = []
        finally:
            self.is_loading = False

    def display(self):
        width = self.terminal.width - 22
        output = []
        
        output.append(f"┬{'─' * (width-2)}┤")
        output.append(f"│{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('Subscribed Subreddits').center(width+21)}│")
        output.append(f"├{'─' * (width-2)}┤")
        
        if not self.reddit_instance:
            output.append(f"│{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('warning')))('Please log in to view your subscribed subreddits').center(width+9)}│")
            output.append(f"╰{'─' * (width-2)}╯")
            return "\n".join(output)
        
        if not self.subreddits:
            output.append(f"│{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('warning')))('No subreddits found').center(width+9)}│")
            output.append(f"╰{'─' * (width-2)}╯")
            return "\n".join(output)
        
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.visible_subreddits, len(self.subreddits))
        
        for idx, subreddit in enumerate(self.subreddits[start_idx:end_idx], start=start_idx + 1):
            if idx - 1 == self.selected_index:
                prefix = self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('highlight')))("│ ► ")
            else:
                prefix = "│   "
            
            subreddit_name = f"r/{subreddit.display_name}"
            subscribers = f"👥 {subreddit.subscribers:,}"
            description = subreddit.public_description or subreddit.description or "No description"
            description = textwrap.shorten(description, width=width-40, placeholder="...")
            
            if prefix == "│   ":
                output.append(f"{prefix}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('title')))(subreddit_name)} | {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('subreddit')))(subscribers)}".ljust(width+42) + "│")
            else:
                output.append(f"{prefix}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('title')))(subreddit_name)} | {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('subreddit')))(subscribers)}".ljust(width+65) + "│")
            output.append(f"│    {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(description)}".ljust(width+24) + "│")
            if idx < end_idx:
                output.append(f"├{'─' * (width-2)}┤")
            else:
                output.append(f"╰{'─' * (width-2)}╯")
        
        output.append(f"")
        
        output.append(f"╭{'─' * (width-2)}╮")
        output.append(f"│{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('Post Category:').center(width+21)}│")
        category_line = "│    "
        for i, category in enumerate(self.post_categories):
            if i == self.selected_category:
                category_line += self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('highlight')))(f"[{category}] ")
            else:
                category_line += self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(f"{category} ")
        output.append(f"{category_line.ljust(width+97)}│")
        output.append(f"╰{'─' * (width-2)}╯")

        output.append(f"")
        
        output.append(f"╭{'─' * (width-2)}╮")
        output.append(f"│{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('Instructions:').center(width+21)}│")
        output.append(f"│    {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• Up/Down Arrow: Navigate subreddits')}".ljust(width+24) + "│")
        output.append(f"│    {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• Left/Right Arrow: Change post category')}".ljust(width+24) + "│")
        output.append(f"│    {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• Enter: Open subreddit')}".ljust(width+24) + "│")
        output.append(f"│    {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• Escape: Return to main screen')}".ljust(width+24) + "│")
        output.append(f"╰{'─' * (width-2)}╯")
        
        if self.is_loading:
            current_time = time.time()
            if current_time - self.last_loading_update >= 0.1:  # Update every 100ms
                self.loading_index = (self.loading_index + 1) % len(self.loading_chars)
                self.last_loading_update = current_time
            loading_text = f"{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('info')))(self.loading_chars[self.loading_index])} Loading..."
            print(self.terminal.move(self.terminal.height - 1, 0) + loading_text)
        
        return "\n".join(output)

    def scroll_up(self):
        if self.selected_index > 0:
            self.selected_index -= 1
            if self.selected_index < self.scroll_offset:
                self.scroll_offset = self.selected_index

    def scroll_down(self):
        if self.selected_index < len(self.subreddits) - 1:
            self.selected_index += 1
            if self.selected_index >= self.scroll_offset + self.visible_subreddits:
                self.scroll_offset = self.selected_index - self.visible_subreddits + 1

    def next_category(self):
        self.selected_category = (self.selected_category + 1) % len(self.post_categories)

    def previous_category(self):
        self.selected_category = (self.selected_category - 1) % len(self.post_categories)

    def get_selected_subreddit(self):
        if 0 <= self.selected_index < len(self.subreddits):
            return self.subreddits[self.selected_index], self.post_categories[self.selected_category]
        return None, None 