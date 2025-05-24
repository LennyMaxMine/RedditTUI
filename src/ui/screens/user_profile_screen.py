from blessed import Terminal
from datetime import datetime

class UserProfileScreen:
    # Rework required
    def __init__(self, term, reddit_instance):
        self.term = term
        self.reddit_instance = reddit_instance
        self.current_user = None
        self.scroll_position = 0
        self.content = []
        self.max_lines = self.term.height - 5
        self.loading = False
        self.error = None

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
                f"╭{'─' * (self.term.width - 2)}╮",
                f"│ {self.current_user.name} {' ' * (self.term.width - len(self.current_user.name) - 4)}│",
                f"├{'─' * (self.term.width - 2)}┤",
                f"│ Karma: {total_karma:,} │ Link: {self.current_user.link_karma:,} │ Comment: {self.current_user.comment_karma:,} │",
                f"│ Created: {created_date} │ Gold: {'✓' if self.current_user.is_gold else '✗'} │ Mod: {'✓' if self.current_user.is_mod else '✗'} │",
                f"╰{'─' * (self.term.width - 2)}╯",
                ""
            ]
            
            self.content.extend(header)
            self.content.append("📝 Recent Posts")
            self.content.append("─" * (self.term.width - 2))
            
            for submission in self.current_user.submissions.new(limit=5):
                title = submission.title[:self.term.width - 10]
                subreddit = submission.subreddit.display_name
                self.content.append(f"• {title}")
                self.content.append(f"  r/{subreddit}")
                self.content.append("")
            
            self.content.append("💬 Recent Comments")
            self.content.append("─" * (self.term.width - 2))
            
            for comment in self.current_user.comments.new(limit=5):
                body = comment.body[:self.term.width - 10].replace('\n', ' ')
                subreddit = comment.subreddit.display_name
                self.content.append(f"• {body}")
                self.content.append(f"  r/{subreddit}")
                self.content.append("")
                
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
            return "Loading profile..."
            
        if self.error:
            return f"Error: {self.error}"
            
        if not self.current_user:
            return "No user profile loaded"
            
        output = []
        visible_content = self.content[self.scroll_position:self.scroll_position + self.max_lines]
        
        for line in visible_content:
            output.append(line)
            
        if len(self.content) > self.max_lines:
            scroll_info = f"Scroll: {self.scroll_position + 1}-{min(self.scroll_position + self.max_lines, len(self.content))}/{len(self.content)}"
            output.append("─" * (self.term.width - 2))
            output.append(scroll_info.center(self.term.width - 2))
            
        return "\n".join(output) 