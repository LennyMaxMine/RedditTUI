from blessed import Terminal

class HelpScreen:
    def __init__(self, terminal):
        self.terminal = terminal
        self.selected_section = 0
        self.sections = ["Navigation", "Post View", "Search", "Account"]
        self.scroll_offset = 0

    def display(self):
        width = self.terminal.width - 22
        output = []
        
        output.append(self.terminal.blue("=" * width))
        output.append(self.terminal.bold_white("Reddit TUI Help".center(width)))
        output.append(self.terminal.blue("=" * width))
        
        # Section navigation
        section_line = "Sections: "
        for i, section in enumerate(self.sections):
            if i == self.selected_section:
                section_line += self.terminal.green(f"[{section}] ")
            else:
                section_line += self.terminal.white(f"{section} ")
        output.append(section_line)
        output.append(self.terminal.blue("-" * width))
        
        # Content based on selected section
        if self.selected_section == 0:  # Navigation
            output.append(self.terminal.cyan("Navigation Controls:"))
            output.append(self.terminal.white("• Up/Down Arrow: Navigate through items"))
            output.append(self.terminal.white("• Left/Right Arrow: Switch between sidebar and content"))
            output.append(self.terminal.white("• Enter: Select item or open post"))
            output.append(self.terminal.white("• Escape: Go back or return to previous screen"))
            output.append(self.terminal.white("• Q: Quit application"))
            output.append("")
            output.append(self.terminal.cyan("Navigation Flow:"))
            output.append(self.terminal.white("1. Start in sidebar"))
            output.append(self.terminal.white("2. Use Right Arrow/Enter to move to post list"))
            output.append(self.terminal.white("3. Use Right Arrow/Enter to open a post"))
            output.append(self.terminal.white("4. Use Left Arrow/Escape to go back"))
            
        elif self.selected_section == 1:  # Post View
            output.append(self.terminal.cyan("Post View Controls:"))
            output.append(self.terminal.white("• Up/Down Arrow: Scroll through comments"))
            output.append(self.terminal.white("• Left Arrow/Escape: Return to post list"))
            output.append(self.terminal.white("• Enter: Load more comments (if available)"))
            output.append("")
            output.append(self.terminal.cyan("Post Information:"))
            output.append(self.terminal.white("• Title and content are displayed at the top"))
            output.append(self.terminal.white("• Metadata shows subreddit, author, score, etc."))
            output.append(self.terminal.white("• Comments are shown below with author and score"))
            
        elif self.selected_section == 2:  # Search
            output.append(self.terminal.cyan("Search Controls:"))
            output.append(self.terminal.white("• Type to enter search query"))
            output.append(self.terminal.white("• Tab: Switch between search types (all/subreddit/user)"))
            output.append(self.terminal.white("• Up/Down Arrow: Navigate search results"))
            output.append(self.terminal.white("• Enter: Open selected post"))
            output.append(self.terminal.white("• Escape: Return to main screen"))
            output.append("")
            output.append(self.terminal.cyan("Search Tips:"))
            output.append(self.terminal.white("• Search is performed as you type"))
            output.append(self.terminal.white("• Results are sorted by relevance"))
            output.append(self.terminal.white("• NSFW content is marked with a red tag"))
            
        elif self.selected_section == 3:  # Account
            output.append(self.terminal.cyan("Account Features:"))
            output.append(self.terminal.white("• Login: Access your Reddit account"))
            output.append(self.terminal.white("• View your subscribed subreddits"))
            output.append(self.terminal.white("• Access your saved posts"))
            output.append("")
            output.append(self.terminal.cyan("Coming Soon:"))
            output.append(self.terminal.yellow("• Multi-account support"))
            output.append(self.terminal.yellow("• Upvote/downvote posts"))
            output.append(self.terminal.yellow("• Save posts"))
            output.append(self.terminal.yellow("• Custom settings"))
        
        output.append(self.terminal.blue("=" * width))
        output.append(self.terminal.cyan("Press Escape to return to main screen"))
        output.append(self.terminal.blue("=" * width))
        
        return "\n".join(output)

    def next_section(self):
        self.selected_section = (self.selected_section + 1) % len(self.sections)

    def previous_section(self):
        self.selected_section = (self.selected_section - 1) % len(self.sections) 