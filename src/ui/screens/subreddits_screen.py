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
        
        output.append(self.terminal.blue("=" * width))
        output.append(self.terminal.bold_white(f"Subscribed Subreddits ({str(len(self.subreddits))})".center(width)))
        output.append(self.terminal.blue("=" * width))
        
        if not self.reddit_instance:
            output.append(self.terminal.yellow("Please log in to view your subscribed subreddits"))
            return "\n".join(output)
        
        if not self.subreddits:
            output.append(self.terminal.yellow("No subreddits found"))
            return "\n".join(output)
        
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.visible_subreddits, len(self.subreddits))
        
        for idx, subreddit in enumerate(self.subreddits[start_idx:end_idx], start=start_idx + 1):
            if idx - 1 == self.selected_index:
                prefix = self.terminal.green("> ")
            else:
                prefix = "  "
            
            subreddit_name = f"r/{subreddit.display_name}"
            subscribers = f"👥 {subreddit.subscribers:,}"
            description = subreddit.public_description or subreddit.description or "No description"
            description = textwrap.shorten(description, width=width-40, placeholder="...")
            
            output.append(f"{prefix}{self.terminal.bold_white(subreddit_name)} | {self.terminal.cyan(subscribers)}")
            output.append(f"    {self.terminal.white(description)}")
            output.append("  " + self.terminal.blue("-" * (width - 2)))
        
        output.append(self.terminal.blue("=" * width))
        output.append(self.terminal.cyan("Post Category:"))
        category_line = "    "
        for i, category in enumerate(self.post_categories):
            if i == self.selected_category:
                category_line += self.terminal.green(f"[{category}] ")
            else:
                category_line += self.terminal.white(f"{category} ")
        output.append(category_line)
        
        output.append(self.terminal.blue("=" * width))
        output.append(self.terminal.cyan("Instructions:"))
        output.append(self.terminal.white("• Up/Down Arrow: Navigate subreddits"))
        output.append(self.terminal.white("• Left/Right Arrow: Change post category"))
        output.append(self.terminal.white("• Enter: Open subreddit"))
        output.append(self.terminal.white("• Escape: Return to main screen"))
        output.append(self.terminal.blue("=" * width))
        
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