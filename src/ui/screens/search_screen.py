from blessed import Terminal
import textwrap
import time
import emoji
from services.theme_service import ThemeService

class SearchScreen:
    def __init__(self, terminal, reddit_instance):
        self.terminal = terminal
        self.reddit_instance = reddit_instance
        self.theme_service = ThemeService()
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
        self.is_loading = False
        self.loading_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.loading_index = 0
        self.last_loading_update = 0

    def contains_emoji(self, text):
            emojis = emoji.emoji_list(text)
            return int(len(emojis))

    def display(self):
        width = self.terminal.width - 22
        output = []
        
        output.append(f"┬{'─' * (width-2)}┤")
        output.append(f"│{self.terminal.bold_white('Reddit Search').center(width-2)}│")
        output.append(f"├{'─' * (width-2)}┤")
        
        output.append(f"│{self.terminal.cyan('Search Query: ')}{self.terminal.white(self.search_query)}{' ' * (width - len(self.search_query) - 16)}│")
        
        type_line = self.terminal.cyan("Search Type: ")
        for i, stype in enumerate(self.search_types):
            if i == self.type_index:
                type_line += self.terminal.green(f"[{stype}] ")
            else:
                type_line += self.terminal.white(f"{stype} ")
        output.append(f"│{type_line}{' ' * (width - len(type_line) + 42)}│")
        
        output.append(f"├{'─' * (width-2)}┤")
        
        if self.search_results:
            start_idx = self.scroll_offset
            end_idx = min(start_idx + self.visible_results, len(self.search_results))
            
            for idx, post in enumerate(self.search_results[start_idx:end_idx], start=start_idx + 1):
                metadata_additional_width = 0
                if idx - 1 == self.selected_index:
                    prefix = self.terminal.green("► ")
                    metadata_additional_width += 11
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
                    metadata_additional_width += 7
                
                if hasattr(post, 'stickied') and post.stickied:
                    metadata += f" | {self.terminal.yellow('📌')}"
                    metadata_additional_width += 7
                
                full_line = post_line + metadata
                if len(full_line) > width - 4:
                    available_space = width - 4 - len(metadata)
                    post_line = f"{prefix}{self.terminal.bold_white(post_num)} {self.terminal.white(title[:available_space-3])}..."
                    full_line = post_line + metadata
                
                output.append(f"│ {full_line}{' ' * (width - len(full_line) + 67 - self.contains_emoji(full_line) + metadata_additional_width)}│")
                if idx < end_idx:
                    output.append(f"├{'─' * (width-2)}┤")
        else:
            if self.is_loading:
                output.append(f"│ {self.terminal.yellow('Searching...')}{' ' * (width - 13)}│")
            else:
                output.append(f"│ {self.terminal.yellow('No search results. Enter a query to search.')}{' ' * (width - 46)}│")
        
        output.append(f"├{'─' * (width-2)}┤")
        output.append(f"│ {self.terminal.cyan('Instructions:')}{' ' * (width - 16)}│")
        output.append(f"│ {self.terminal.white('• Type to enter search query')}{' ' * (width - 31)}│")
        output.append(f"│ {self.terminal.white('• Tab to switch search type')}{' ' * (width - 30)}│")
        output.append(f"│ {self.terminal.white('• Up/Down to navigate results')}{' ' * (width - 32)}│")
        output.append(f"│ {self.terminal.white('• Enter to select result')}{' ' * (width - 27)}│")
        output.append(f"│ {self.terminal.white('• Esc to return to main screen')}{' ' * (width - 33)}│")
        output.append(f"╰{'─' * (width-2)}╯")
        
        if self.is_loading:
            current_time = time.time()
            if current_time - self.last_loading_update >= 0.1:  # Update every 100ms
                self.loading_index = (self.loading_index + 1) % len(self.loading_chars)
                self.last_loading_update = current_time
            loading_text = f"{self.terminal.bright_blue(self.loading_chars[self.loading_index])} Loading..."
            print(self.term.move(self.term.height - 1, 0) + loading_text)
        
        return "\n".join(output)

    def add_char(self, char):
        if not isinstance(char, str) or len(char) != 1:
            return
            
        self.search_query += char
        self.pending_search = True
        current_time = time.time()
        if current_time - self.last_search_time >= self.search_delay:
            try:
                self.search()
                self.last_search_time = current_time
                self.pending_search = False
            except Exception as e:
                self.terminal.move(self.terminal.height - 3, 0)
                print(self.terminal.red(f"Error adding character: {str(e)}"))
                self.terminal.move(0, 0)

    def backspace(self):
        if not self.search_query:
            return
            
        self.search_query = self.search_query[:-1]
        self.pending_search = True
        current_time = time.time()
        if current_time - self.last_search_time >= self.search_delay:
            try:
                self.search()
                self.last_search_time = current_time
                self.pending_search = False
            except Exception as e:
                self.terminal.move(self.terminal.height - 3, 0)
                print(self.terminal.red(f"Error handling backspace: {str(e)}"))
                self.terminal.move(0, 0)

    def clear_query(self):
        self.search_query = ""
        self.search_results = []
        self.selected_index = 0
        self.scroll_offset = 0

    def search(self):
        if not self.search_query or not self.reddit_instance:
            return
        
        self.is_loading = True
        try:
            if self.search_type == "all":
                self.search_results = list(self.reddit_instance.subreddit("all").search(
                    self.search_query, limit=25, sort="relevance", syntax="lucene"
                ))
            elif self.search_type == "subreddit":
                subreddits = list(self.reddit_instance.subreddits.search(self.search_query, limit=25))
                self.search_results = []
                for subreddit in subreddits:
                    try:
                        posts = list(subreddit.hot(limit=1))
                        if posts:
                            self.search_results.extend(posts)
                    except:
                        continue
            elif self.search_type == "user":
                users = list(self.reddit_instance.redditors.search(self.search_query, limit=25))
                self.search_results = []
                for user in users:
                    try:
                        posts = list(user.submissions.new(limit=1))
                        if posts:
                            self.search_results.extend(posts)
                    except:
                        continue
            
            self.selected_index = 0
            self.scroll_offset = 0
        except Exception as e:
            self.search_results = []
            self.terminal.move(self.terminal.height - 3, 0)
            print(self.terminal.red(f"Error performing search: {str(e)}"))
            self.terminal.move(0, 0)
        finally:
            self.is_loading = False

    def scroll_up(self):
        if self.selected_index > 0:
            self.selected_index -= 1
            if self.selected_index < self.scroll_offset:
                self.scroll_offset = self.selected_index

    def scroll_down(self):
        if self.selected_index < len(self.search_results) - 1:
            self.selected_index += 1
            if self.selected_index >= self.scroll_offset + self.visible_results:
                self.scroll_offset = self.selected_index - self.visible_results + 1

    def next_search_type(self):
        self.type_index = (self.type_index + 1) % len(self.search_types)
        self.search_type = self.search_types[self.type_index]
        self.search()

    def get_selected_post(self):
        if 0 <= self.selected_index < len(self.search_results):
            post = self.search_results[self.selected_index]
            post.origin = f"Search: {self.search_query}"
            return post
        return None 