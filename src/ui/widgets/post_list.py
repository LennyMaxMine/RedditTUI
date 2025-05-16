from blessed import Terminal

class PostList:
    def __init__(self, terminal):
        self.terminal = terminal
        self.posts = []
        self.selected_index = 0
        self.visible_posts = 10
        self.scroll_offset = 0

    def display(self):
        if not self.posts:
            return "No posts available"
        
        width = self.terminal.width
        output = []
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
            
            post_line = f"{prefix}{idx}. {post.title}"
            if len(post_line) > width - 4:
                post_line = post_line[:width-7] + "..."
            output.append(post_line)
        
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