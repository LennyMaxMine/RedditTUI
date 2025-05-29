from blessed import Terminal
from services.theme_service import ThemeService
import math

class ThemeScreen:
    def __init__(self, terminal):
        self.terminal = terminal
        self.theme_service = ThemeService()
        self.selected_index = 0
        self.scroll_offset = 0
        self.visible_themes = 5
        self.themes = self.theme_service.get_available_themes()
        self.current_theme = self.theme_service.get_current_theme()
        self.running = True

    def get_display(self):
        width = self.terminal.width - 22
        output = []
        
        output.append(f"┌{'─' * (width-2)}┐")
        output.append(f"│{self.terminal.bright_blue('Theme Selection').center(width)}│")
        
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.visible_themes, len(self.themes))
        
        for idx, theme_name in enumerate(self.themes[start_idx:end_idx], start=start_idx):
            if idx == self.selected_index:
                prefix = self.terminal.bright_green("│ ► ")
            else:
                prefix = "│   "
            
            theme = self.theme_service.themes[theme_name]
            is_current = theme_name == self.current_theme
            
            theme_line = f"{prefix}{self.terminal.bold_white(theme_name)}"
            if is_current:
                theme_line += f" {self.terminal.green('(Current)')}"
            output.append(f"│{'─' * (width-2)}│")
            output.append(f"{theme_line.ljust(width)}│")
            
            title_color = theme.get('title', '#ffffff')
            hexrgb = self._hex_to_rgb(title_color)
            output.append(f"│    {self.terminal.color_rgb(*hexrgb[0])('Title Text').ljust(width - 4)}│{hexrgb[1]}")
            
            subreddit_color = theme.get('subreddit', '#ffffff')
            author_color = theme.get('author', '#ffffff')
            subreddit_hexrgb = self._hex_to_rgb(subreddit_color)
            author_hexrgb = self._hex_to_rgb(author_color)
            output.append(f"│    {self.terminal.color_rgb(*subreddit_hexrgb[0])('r/subreddit')} | {self.terminal.color_rgb(*author_hexrgb[0])('u/author')}".ljust(width - 4) + f"│{hexrgb[1]}")
            
            score_color = theme.get('score', '#ffffff')
            comments_color = theme.get('comments', '#ffffff')
            score_hexrgb = self._hex_to_rgb(score_color)
            comments_hexrgb = self._hex_to_rgb(comments_color)
            output.append(f"│    {self.terminal.color_rgb(*score_hexrgb[0])('↑123')} | {self.terminal.color_rgb(*comments_hexrgb[0])('💬45')}".ljust(width - 4) + f"│{hexrgb[1]}")
            
            content_color = theme.get('content', '#ffffff')
            content_hexrgb = self._hex_to_rgb(content_color)
            output.append(f"│    {self.terminal.color_rgb(*content_hexrgb[0])('This is a sample post content...').ljust(width - 4)}│{hexrgb[1]}")
            
            if idx == end_idx - 1:
                output.append(f"└{'─' * (width-2)}┘")
        
        output.append(f"")
        output.append(f"╭{'─' * (width-2)}╮")
        output.append(f"│{self.terminal.bright_cyan('Instructions:').center(width)}│")
        output.append(f"│    {self.terminal.white('• Up/Down Arrow: Navigate themes').ljust(width - 4)}│")
        output.append(f"│    {self.terminal.white('• Enter: Select theme').ljust(width - 4)}│")
        output.append(f"│    {self.terminal.white('• Escape: Return to settings').ljust(width - 4)}│")
        output.append(f"╰{'─' * (width-2)}╯")
        
        return "\n".join(output)

    def _hex_to_rgb(self, hex_color):
        if not hex_color or not isinstance(hex_color, str):
            rgb = (255, 255, 255)
            return rgb, sum(len(str(num)) for num in rgb)
        
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join(c*2 for c in hex_color)
        
        try:
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            return rgb, sum(len(str(num)) for num in rgb)
        except ValueError:
            rgb = (255, 255, 255)
            return rgb, sum(len(str(num)) for num in rgb)

    def scroll_up(self):
        if self.selected_index > 0:
            self.selected_index -= 1
            if self.selected_index < self.scroll_offset:
                self.scroll_offset = self.selected_index

    def scroll_down(self):
        if self.selected_index < len(self.themes) - 1:
            self.selected_index += 1
            if self.selected_index >= self.scroll_offset + self.visible_themes:
                self.scroll_offset = self.selected_index - self.visible_themes + 1

    def select_theme(self):
        if 0 <= self.selected_index < len(self.themes):
            selected_theme = self.themes[self.selected_index]
            self.theme_service.set_theme(selected_theme)
            self.current_theme = selected_theme
            return selected_theme
        return None 