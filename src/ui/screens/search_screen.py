from blessed import Terminal
import textwrap
import time

class SearchScreen:
    def __init__(self, terminal, reddit_instance):
        self.terminal = terminal
        self.reddit_instance = reddit_instance
        self.search_query = ""
        self.search_results = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.visible_results = 10
        self.search_type = "all"
        self.search_types = ["all", "subreddit", "user"]
        self.type_index = 0
        self.last_search_time = 0
        self.search_delay = 0.5  # 500ms delay between searches
        self.pending_search = False

    def display(self):
        width = self.terminal.width - 22
        output = []
        
        output.append(self.terminal.blue("=" * width))
        output.append(self.terminal.bold_white("Reddit Search".center(width)))
        output.append(self.terminal.blue("=" * width))
        
        output.append(self.terminal.cyan("Search Query: ") + self.terminal.white(self.search_query))
        
        type_line = self.terminal.cyan("Search Type: ")
        for i, stype in enumerate(self.search_types):
            if i == self.type_index:
                type_line += self.terminal.green(f"[{stype}] ")
            else:
                type_line += self.terminal.white(f"{stype} ")
        output.append(type_line)
        
        output.append(self.terminal.blue("-" * width))
        
        # Search results
        if self.search_results:
            start_idx = self.scroll_offset
            end_idx = min(start_idx + self.visible_results, len(self.search_results))
            
            for idx, post in enumerate(self.search_results[start_idx:end_idx], start=start_idx + 1):
                if idx - 1 == self.selected_index:
                    prefix = self.terminal.green("> ")
                else:
                    prefix = "  "
                
                post_num = f"{idx}."
                title = post.title
                if len(title) > width - 40:
                    title = title[:width-43] + "..."
                
                subreddit = self.terminal.cyan(f"r/{post.subreddit.display_name}")
                author = self.terminal.yellow(f"u/{post.author}")
                score = self.terminal.green(f"↑{post.score}")
                comments = self.terminal.magenta(f"💬{post.num_comments}")
                
                post_line = f"{prefix}{self.terminal.bold_white(post_num)} {self.terminal.white(title)}"
                metadata = f" | {subreddit} | {author} | {score} | {comments}"
                
                if hasattr(post, 'over_18') and post.over_18:
                    metadata += f" | {self.terminal.red('NSFW')}"
                
                if hasattr(post, 'stickied') and post.stickied:
                    metadata += f" | {self.terminal.yellow('📌')}"
                
                full_line = post_line + metadata
                if len(full_line) > width - 2:
                    available_space = width - 2 - len(metadata)
                    post_line = f"{prefix}{self.terminal.bold_white(post_num)} {self.terminal.white(title[:available_space-3])}..."
                    full_line = post_line + metadata
                
                output.append(full_line)
                output.append("  " + self.terminal.blue("-" * (width - 2)))
        else:
            output.append(self.terminal.yellow("No search results. Enter a query to search."))
        
        # Instructions
        output.append(self.terminal.blue("=" * width))
        output.append(self.terminal.cyan("Instructions:"))
        output.append(self.terminal.white("• Type to enter search query"))
        output.append(self.terminal.white("• Tab to switch search type"))
        output.append(self.terminal.white("• Up/Down to navigate results"))
        output.append(self.terminal.white("• Enter to select result"))
        output.append(self.terminal.white("• Esc to return to main screen"))
        output.append(self.terminal.blue("=" * width))
        
        return "\n".join(output)

    def add_char(self, char):
        """Add a character to the search query"""
        self.search_query += char
        self.pending_search = True
        current_time = time.time()
        if current_time - self.last_search_time >= self.search_delay:
            self.search()
            self.last_search_time = current_time
            self.pending_search = False

    def backspace(self):
        """Remove the last character from the search query"""
        self.search_query = self.search_query[:-1]

    def clear_query(self):
        """Clear the search query"""
        self.search_query = ""

    def search(self):
        """Perform the search using Reddit's API"""
        if not self.search_query or not self.reddit_instance or not self.pending_search:
            return
        
        try:
            if self.search_type == "all":
                self.search_results = list(self.reddit_instance.subreddit("all").search(
                    self.search_query, limit=25, sort="relevance", syntax="lucene"
                ))
            elif self.search_type == "subreddit":
                self.search_results = list(self.reddit_instance.front.search(
                    self.search_query, limit=25, sort="relevance", syntax="lucene"
                ))
            elif self.search_type == "user":
                self.search_results = list(self.reddit_instance.user.me().submissions.search(
                    self.search_query, limit=25, sort="relevance", syntax="lucene"
                ))
            
            self.selected_index = 0
            self.scroll_offset = 0
        except Exception as e:
            self.search_results = []
            print(self.terminal.move(self.terminal.height - 3, 0) + 
                  self.terminal.red(f"Error performing search: {e}"))

    def scroll_up(self):
        """Scroll the results up"""
        if self.selected_index > 0:
            self.selected_index -= 1
            if self.selected_index < self.scroll_offset:
                self.scroll_offset = self.selected_index

    def scroll_down(self):
        """Scroll the results down"""
        if self.selected_index < len(self.search_results) - 1:
            self.selected_index += 1
            if self.selected_index >= self.scroll_offset + self.visible_results:
                self.scroll_offset = self.selected_index - self.visible_results + 1

    def next_search_type(self):
        """Switch to the next search type"""
        self.type_index = (self.type_index + 1) % len(self.search_types)
        self.search_type = self.search_types[self.type_index]

    def get_selected_post(self):
        """Get the currently selected post"""
        if 0 <= self.selected_index < len(self.search_results):
            return self.search_results[self.selected_index]
        return None 