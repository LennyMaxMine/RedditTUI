from blessed import Terminal
from services.theme_service import ThemeService

class HelpScreen:
    def __init__(self, terminal):
        self.terminal = terminal
        self.theme_service = ThemeService()
        self.selected_section = 0
        self.sections = ["Navigation", "Post View", "Search", "Account"]
        self.scroll_offset = 0

    def display(self):
        width = self.terminal.width - 22
        output = []
        
        output.append(f"┬{'─' * (width-2)}┤")
        output.append(f"│{self.terminal.bright_blue('Reddit TUI Help').center(width+9)}│")
        output.append(f"├{'─' * (width-2)}┤")
        
        # Section navigation
        section_line = "│ Sections: "
        for i, section in enumerate(self.sections):
            if i == self.selected_section:
                section_line += self.terminal.bright_green(f"[{section}] ")
            else:
                section_line += self.terminal.white(f"{section} ")
        output.append(f"{section_line.ljust(width+43)}│")
        output.append(f"├{'─' * (width-2)}┤")
        
        # Content based on selected section
        if self.selected_section == 0:  # Navigation
            output.append(f"│{self.terminal.bright_cyan('Navigation Controls:').center(width+9)}│")
            output.append(f"│    {self.terminal.white('• Up/Down Arrow: Navigate through items')}".ljust(width+10) + "│")
            output.append(f"│    {self.terminal.white('• Left/Right Arrow: Switch between sidebar and content')}".ljust(width+10) + "│")
            output.append(f"│    {self.terminal.white('• Enter: Select item or open post')}".ljust(width+10) + "│")
            output.append(f"│    {self.terminal.white('• Escape: Go back or return to previous screen')}".ljust(width+10) + "│")
            output.append(f"│    {self.terminal.white('• Q: Quit application')}".ljust(width+10) + "│")
            output.append(f"│".ljust(width-1) + "│")
            output.append(f"├{'─' * (width-2)}┤")
            output.append(f"│{self.terminal.bright_cyan('Navigation Flow:').center(width+9)}│")
            output.append(f"│    {self.terminal.white('1. Start in sidebar')}".ljust(width+10) + "│")
            output.append(f"│    {self.terminal.white('2. Use Right Arrow/Enter to move to post list')}".ljust(width+10) + "│")
            output.append(f"│    {self.terminal.white('3. Use Right Arrow/Enter to open a post')}".ljust(width+10) + "│")
            output.append(f"│    {self.terminal.white('4. Use Left Arrow/Escape to go back')}".ljust(width+10) + "│")
            output.append(f"│".ljust(width-1) + "│")
            
        elif self.selected_section == 1:  # Post View
            output.append(f"│{self.terminal.bright_cyan('Post View Controls:').center(width+9)}│")
            output.append(f"│    {self.terminal.white('• Up/Down Arrow: Scroll through comments')}".ljust(width+10) + "│")
            output.append(f"│    {self.terminal.white('• Left Arrow/Escape: Return to post list')}".ljust(width+10) + "│")
            output.append(f"│    {self.terminal.white('• Enter: Load more comments (if available)')}".ljust(width+10) + "│")
            output.append(f"│".ljust(width-1) + "│")
            output.append(f"├{'─' * (width-2)}┤")
            output.append(f"│{self.terminal.bright_cyan('Post Information:').center(width+9)}│")
            output.append(f"│    {self.terminal.white('• Title and content are displayed at the top')}".ljust(width+10) + "│")
            output.append(f"│    {self.terminal.white('• Metadata shows subreddit, author, score, etc.')}".ljust(width+10) + "│")
            output.append(f"│    {self.terminal.white('• Comments are shown below with author and score')}".ljust(width+10) + "│")
            output.append(f"│".ljust(width-1) + "│")
            
        elif self.selected_section == 2:  # Search
            output.append(f"│{self.terminal.bright_cyan('Search Controls:').center(width+9)}│")
            output.append(f"│    {self.terminal.white('• Type to enter search query')}".ljust(width+10) + "│")
            output.append(f"│    {self.terminal.white('• Tab: Switch between search types (all/subreddit/user)')}".ljust(width+10) + "│")
            output.append(f"│    {self.terminal.white('• Up/Down Arrow: Navigate search results')}".ljust(width+10) + "│")
            output.append(f"│    {self.terminal.white('• Enter: Open selected post')}".ljust(width+10) + "│")
            output.append(f"│    {self.terminal.white('• Escape: Return to main screen')}".ljust(width+10) + "│")
            output.append(f"│".ljust(width-1) + "│")
            output.append(f"├{'─' * (width-2)}┤")
            output.append(f"│{self.terminal.bright_cyan('Search Tips:').center(width+9)}│")
            output.append(f"│    {self.terminal.white('• Search is performed as you type')}".ljust(width+10) + "│")
            output.append(f"│    {self.terminal.white('• Results are sorted by relevance')}".ljust(width+10) + "│")
            output.append(f"│    {self.terminal.white('• NSFW content is marked with a red tag')}".ljust(width+10) + "│")
            output.append(f"│".ljust(width-1) + "│")
            
        elif self.selected_section == 3:  # Account
            output.append(f"│{self.terminal.bright_cyan('Account Features:').center(width+9)}│")
            output.append(f"│    {self.terminal.white('• Login: Access your Reddit account')}".ljust(width+10) + "│")
            output.append(f"│    {self.terminal.white('• View your subscribed subreddits')}".ljust(width+10) + "│")
            output.append(f"│    {self.terminal.white('• Access your saved posts')}".ljust(width+10) + "│")
            output.append(f"│".ljust(width-1) + "│")
            output.append(f"├{'─' * (width-2)}┤")
            output.append(f"│{self.terminal.bright_cyan('Coming Soon:').center(width+9)}│")
            output.append(f"│    {self.terminal.yellow('• Multi-account support')}".ljust(width+10) + "│")
            output.append(f"│    {self.terminal.yellow('• Upvote/downvote posts')}".ljust(width+10) + "│")
            output.append(f"│    {self.terminal.yellow('• Save posts')}".ljust(width+10) + "│")
            output.append(f"│    {self.terminal.yellow('• Custom settings')}".ljust(width+10) + "│")
            output.append(f"│".ljust(width-1) + "│")
        
        output.append(f"╰{'─' * (width-2)}╯")
        output.append(f"")
        
        return "\n".join(output)

    def next_section(self):
        self.selected_section = (self.selected_section + 1) % len(self.sections)

    def previous_section(self):
        self.selected_section = (self.selected_section - 1) % len(self.sections) 