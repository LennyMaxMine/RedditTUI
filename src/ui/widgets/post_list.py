from blessed import Terminal
import textwrap

class PostList:
    def __init__(self, terminal):
        self.terminal = terminal
        self.posts = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.visible_posts = 10

    def display(self):
        if not self.posts:
            return "No posts available"
        
        # Calculate width accounting for sidebar and margins
        width = self.terminal.width - 24  # Account for sidebar (20) and margins (4)
        output = []
        
        # Header
        output.append("=" * width)
        output.append("Reddit Posts".center(width))
        output.append("=" * width)
        
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.visible_posts, len(self.posts))
        
        for idx, post in enumerate(self.posts[start_idx:end_idx], start=start_idx + 1):
            if idx - 1 == self.selected_index:
                prefix = "> "
            else:
                prefix = "  "
            
            # Title line
            title = post.title
            if len(title) > width - 4:
                title = title[:width-7] + "..."
            output.append(f"{prefix}{title}")
            
            # Metadata line
            metadata = []
            metadata.append(f"r/{post.subreddit.display_name}")
            metadata.append(f"u/{post.author}")
            metadata.append(f"↑{post.score}")
            metadata.append(f"💬{post.num_comments}")
            
            if hasattr(post, 'over_18') and post.over_18:
                metadata.append("NSFW")
            if hasattr(post, 'stickied') and post.stickied:
                metadata.append("📌")
            
            # Format metadata with proper spacing
            metadata_line = "    " + " | ".join(metadata)
            output.append(metadata_line)
            
            # Description line (if available)
            if hasattr(post, 'selftext') and post.selftext:
                try:
                    # Clean and wrap the description
                    desc = post.selftext.replace('\n', ' ').strip()
                    # Remove any control characters
                    desc = ''.join(char for char in desc if ord(char) >= 32 or char == '\n')
                    # Wrap the text
                    wrapped_desc = textwrap.wrap(desc, width=width-6)
                    # Take only the first line if it's too long
                    if wrapped_desc:
                        first_line = wrapped_desc[0]
                        if len(first_line) > width - 6:
                            first_line = first_line[:width-9] + "..."
                        output.append(f"    {first_line}")
                except Exception:
                    # If anything goes wrong with the description, skip it
                    pass
            
            # Add a separator line between posts
            output.append("  " + "-" * (width - 2))
        
        return "\n".join(output)

    def get_selected_post(self):
        if 0 <= self.selected_index < len(self.posts):
            return self.posts[self.selected_index]
        return None

    def update_posts(self, new_posts):
        self.posts = new_posts
        self.selected_index = 0
        self.scroll_offset = 0

    def scroll_up(self):
        if self.selected_index > 0:
            self.selected_index -= 1
            if self.selected_index < self.scroll_offset:
                self.scroll_offset = self.selected_index

    def scroll_down(self):
        if self.selected_index < len(self.posts) - 1:
            self.selected_index += 1
            if self.selected_index >= self.scroll_offset + self.visible_posts:
                self.scroll_offset = self.selected_index - self.visible_posts + 1