from blessed import Terminal
import textwrap

class SubredditsScreen:
    def __init__(self, terminal, reddit_instance):
        self.terminal = terminal
        self.reddit_instance = reddit_instance
        self.selected_index = 0
        self.scroll_offset = 0
        self.visible_subreddits = 10
        self.subreddits = []
        self.post_categories = ["hot", "new", "top", "rising"]
        self.selected_category = 0
        self.load_subreddits()

    def load_subreddits(self):
        if not self.reddit_instance:
            return
        
        try:
            self.subreddits = list(self.reddit_instance.user.subreddits(limit=None))
            self.selected_index = 0
            self.scroll_offset = 0
        except Exception as e:
            print(self.terminal.move(self.terminal.height - 3, 0) + 
                  self.terminal.red(f"Error loading subreddits: {e}"))
            

    def display(self):
        width = self.terminal.width - 22
        output = []
        
        output.append(f"┬{'─' * (width-2)}┤")
        output.append(f"│{self.terminal.bright_blue('Subscribed Subreddits').center(width+9)}│")
        output.append(f"├{'─' * (width-2)}┤")
        
        if not self.reddit_instance:
            output.append(f"│{self.terminal.yellow('Please log in to view your subscribed subreddits').center(width+9)}│")
            output.append(f"╰{'─' * (width-2)}╯")
            return "\n".join(output)
        
        if not self.subreddits:
            output.append(f"│{self.terminal.yellow('No subreddits found').center(width+9)}│")
            output.append(f"╰{'─' * (width-2)}╯")
            return "\n".join(output)
        
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.visible_subreddits, len(self.subreddits))
        
        for idx, subreddit in enumerate(self.subreddits[start_idx:end_idx], start=start_idx + 1):
            if idx - 1 == self.selected_index:
                prefix = self.terminal.bright_green("│ ► ")
            else:
                prefix = "│   "
            
            subreddit_name = f"r/{subreddit.display_name}"
            subscribers = f"👥 {subreddit.subscribers:,}"
            description = subreddit.public_description or subreddit.description or "No description"
            description = textwrap.shorten(description, width=width-40, placeholder="...")
            
            if prefix == "│   ":
                output.append(f"{prefix}{self.terminal.bold_white(subreddit_name)} | {self.terminal.cyan(subscribers)}".ljust(width+24) + "│")
            else:
                output.append(f"{prefix}{self.terminal.bold_white(subreddit_name)} | {self.terminal.cyan(subscribers)}".ljust(width+35) + "│")
            output.append(f"│    {self.terminal.white(description)}".ljust(width+10) + "│")
            if idx < end_idx:
                output.append(f"├{'─' * (width-2)}┤")
            else:
                output.append(f"╰{'─' * (width-2)}╯")
        
        output.append(f"")
        
        output.append(f"╭{'─' * (width-2)}╮")
        output.append(f"│{self.terminal.bright_cyan('Post Category:').center(width+9)}│")
        category_line = "│    "
        for i, category in enumerate(self.post_categories):
            if i == self.selected_category:
                category_line += self.terminal.bright_green(f"[{category}] ")
            else:
                category_line += self.terminal.white(f"{category} ")
        output.append(f"{category_line.ljust(width+43)}│")
        output.append(f"╰{'─' * (width-2)}╯")

        output.append(f"")
        
        output.append(f"╭{'─' * (width-2)}╮")
        output.append(f"│{self.terminal.bright_cyan('Instructions:').center(width+9)}│")
        output.append(f"│    {self.terminal.white('• Up/Down Arrow: Navigate subreddits')}".ljust(width+10) + "│")
        output.append(f"│    {self.terminal.white('• Left/Right Arrow: Change post category')}".ljust(width+10) + "│")
        output.append(f"│    {self.terminal.white('• Enter: Open subreddit')}".ljust(width+10) + "│")
        output.append(f"│    {self.terminal.white('• Escape: Return to main screen')}".ljust(width+10) + "│")
        output.append(f"╰{'─' * (width-2)}╯")
        
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