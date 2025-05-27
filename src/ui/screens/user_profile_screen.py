from blessed import Terminal
from datetime import datetime

class UserProfileScreen:
    def __init__(self, term, reddit_instance):
        self.term = term
        self.reddit_instance = reddit_instance
        self.current_user = None
        self.scroll_position = 0
        self.content = []
        self.max_lines = self.term.height - 5
        self.loading = False
        self.error = None
        self.width = self.term.width - 22

    def load_user(self, username):
        self.loading = True
        self.error = None
        try:
            self.current_user = self.reddit_instance.redditor(username)
            self.content = []
            self.scroll_position = 0
            
            created_date = datetime.fromtimestamp(self.current_user.created_utc).strftime('%Y-%m-%d')
            total_karma = self.current_user.link_karma + self.current_user.comment_karma
            
            header = [
                f"┬{'─' * (self.width-2)}┤",
                f"│{self.term.bright_blue(f'User Profile: {self.current_user.name}').center(self.width+9)}│",
                f"├{'─' * (self.width-2)}┤",
                f"│{self.term.bright_cyan(f'Karma: {total_karma:,}').ljust(self.width//2)}│{self.term.bright_yellow(f'Link: {self.current_user.link_karma:,}').ljust(self.width//2+19)}│",
                f"│{self.term.bright_cyan(f'Comment: {self.current_user.comment_karma:,}').ljust(self.width//2)}│{self.term.bright_yellow(f'Created: {created_date}').ljust(self.width//2+19)}│",
                f"│{self.term.bright_cyan(f'Gold: {self.term.bright_yellow("✓") if self.current_user.is_gold else self.term.red("✗")}').ljust(self.width//2)}│{self.term.bright_yellow(f'Mod: {self.term.bright_green("✓") if self.current_user.is_mod else self.term.red("✗")}').ljust(self.width//2-2)}│",
                f"├{'─' * (self.width-2)}┤"
            ]
            
            self.content.extend(header)
            self.content.append(f"│{self.term.bright_blue('📝 Recent Posts').center(self.width+8)}│")
            self.content.append(f"├{'─' * (self.width-2)}┤")
            
            for submission in self.current_user.submissions.new(limit=5):
                title = submission.title[:self.width - 10]
                subreddit = submission.subreddit.display_name
                score = submission.score
                self.content.append(f"│ {self.term.bold_white(f'• {title}')}".ljust(self.width+14) + "│")
                self.content.append(f"│ {self.term.bright_cyan(f'r/{subreddit}')} | {self.term.bright_yellow(f'Score: {score:,}')}".ljust(self.width+21) + "│")
                self.content.append(f"├{'─' * (self.width-2)}┤")
            
            self.content.append(f"│{self.term.bright_blue('💬 Recent Comments').center(self.width+8)}│")
            self.content.append(f"├{'─' * (self.width-2)}┤")
            
            for comment in self.current_user.comments.new(limit=5):
                body = comment.body[:self.width - 10].replace('\n', ' ')
                subreddit = comment.subreddit.display_name
                score = comment.score
                self.content.append(f"│ {self.term.bold_white(f'• {body}')}".ljust(self.width+14) + "│")
                self.content.append(f"│ {self.term.bright_cyan(f'r/{subreddit}')} | {self.term.bright_yellow(f'Score: {score:,}')}".ljust(self.width+21) + "│")
                self.content.append(f"├{'─' * (self.width-2)}┤")
            
            self.content.append(f"╰{'─' * (self.width-2)}╯")
                
        except Exception as e:
            self.error = str(e)
            self.content = []
        finally:
            self.loading = False

    def scroll_up(self):
        if self.scroll_position > 0:
            self.scroll_position = max(0, self.scroll_position - 3)

    def scroll_down(self):
        if self.scroll_position < len(self.content) - self.max_lines:
            self.scroll_position = min(len(self.content) - self.max_lines, self.scroll_position + 3)

    def display(self):
        if self.loading:
            return f"╭{'─' * (self.width-2)}╮\n│{self.term.bright_blue('Loading profile...').center(self.width+9)}│\n╰{'─' * (self.width-2)}╯"
            
        if self.error:
            return f"╭{'─' * (self.width-2)}╮\n│{self.term.red(f'Error: {self.error}').center(self.width+9)}│\n╰{'─' * (self.width-2)}╯"
            
        if not self.current_user:
            return f"╭{'─' * (self.width-2)}╮\n│{self.term.yellow('No user profile loaded').center(self.width+9)}│\n╰{'─' * (self.width-2)}╯"
            
        output = []
        visible_content = self.content[self.scroll_position:self.scroll_position + self.max_lines]
        
        for line in visible_content:
            output.append(line)
            
        if len(self.content) > self.max_lines:
            scroll_info = f"Scroll: {self.scroll_position + 1}-{min(self.scroll_position + self.max_lines, len(self.content))}/{len(self.content)}"
            output.append(f"╭{'─' * (self.width-2)}╮")
            output.append(f"│{self.term.bright_blue(scroll_info).center(self.width+9)}│")
            output.append(f"╰{'─' * (self.width-2)}╯")
            
        return "\n".join(output) 