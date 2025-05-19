from blessed import Terminal
import textwrap

class PostList:
    def __init__(self, terminal, visible_posts=10):
        self.terminal = terminal
        self.posts = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.visible_posts = visible_posts
        self.loading_more = False

    def display(self):
        if not self.posts:
            return "No posts available"
        
        # Calculate width accounting for sidebar and margins
        width = self.terminal.width - 24  # Account for sidebar (20) and margins (4)
        output = []
        
        # Header
        output.append(self.terminal.blue("=" * width))
        output.append(self.terminal.blue("Reddit Posts".center(width)))
        output.append(self.terminal.blue("=" * width))
        
        # Calculate how many posts we can show based on screen height
        # Each post takes 4 lines (title, metadata, description, separator)
        posts_per_screen = (self.terminal.height - 6) // 4  # Subtract header and margins
        self.visible_posts = max(5, posts_per_screen)  # Ensure at least 5 posts are visible
        
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.visible_posts, len(self.posts))
        
        for idx, post in enumerate(self.posts[start_idx:end_idx], start=start_idx + 1):
            if idx - 1 == self.selected_index:
                prefix = self.terminal.green("> ")
            else:
                prefix = "  "
            
            # Title line
            title = post.title
            if len(title) > width - 4:
                title = title[:width-7] + "..."
            output.append(f"{prefix}{self.terminal.bold_white(title)}")
            
            # Metadata line
            metadata = []
            metadata.append(self.terminal.cyan(f"r/{post.subreddit.display_name}"))
            metadata.append(self.terminal.yellow(f"u/{post.author}"))
            # Check for image post and add it right after author
            if hasattr(post, 'url') and any(post.url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                metadata.append(self.terminal.blue("🖼️"))
            metadata.append(self.terminal.green(f"↑{post.score}"))
            metadata.append(self.terminal.magenta(f"💬{post.num_comments}"))
            
            if hasattr(post, 'over_18') and post.over_18:
                metadata.append(self.terminal.red("NSFW"))
            if hasattr(post, 'stickied') and post.stickied:
                metadata.append(self.terminal.yellow("📌"))
            
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
                        output.append(f"    {self.terminal.dim(first_line)}")
                except Exception:
                    # If anything goes wrong with the description, skip it
                    pass
            
            # Add a separator line between posts
            output.append("  " + self.terminal.blue("-" * (width - 2)))
        
        return "\n".join(output)

    def get_selected_post(self):
        if 0 <= self.selected_index < len(self.posts):
            return self.posts[self.selected_index]
        return None

    def append_posts(self, new_posts):
        """Append new posts to the existing list without resetting the view"""
        self.posts.extend(new_posts)

    def update_posts(self, new_posts):
        """Replace all posts and reset the view"""
        self.posts = new_posts
        self.selected_index = 0
        self.scroll_offset = 0

    def scroll_down(self):
        if self.selected_index < len(self.posts) - 1:
            self.selected_index += 1
            if self.selected_index >= self.scroll_offset + self.visible_posts:
                self.scroll_offset = self.selected_index - self.visible_posts + 1
            # If we're near the end of the current posts, trigger loading more
            if self.selected_index >= len(self.posts) - 5 and not self.loading_more:
                self.loading_more = True
                return True  # Signal that more posts should be loaded
        return False

    def scroll_up(self):
        if self.selected_index > 0:
            self.selected_index -= 1
            if self.selected_index < self.scroll_offset:
                self.scroll_offset = self.selected_index