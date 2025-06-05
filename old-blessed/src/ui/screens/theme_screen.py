from blessed import Terminal
import textwrap
from services.theme_service import ThemeService
import math

class ThemeScreen:
    def __init__(self, terminal):
        self.terminal = terminal
        self.theme_service = ThemeService()
        self.selected_index = 0
        self.scroll_offset = 0
        self.visible_themes = 10
        self.themes = self.theme_service.get_available_themes()
        self.current_theme = self.theme_service.get_current_theme()
        self.running = True

    def get_display(self):
        width = self.terminal.width - 22
        output = []
        
        output.append(f"┬{'─' * (width-2)}┤")
        title = self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('Theme Selection')
        output.append(f"│{title.center(width+21)}│")
        output.append(f"├{'─' * (width-2)}┤")
        
        if not self.themes:
            output.append(f"│{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('warning')))('No themes available').center(width+21)}│")
            output.append(f"╰{'─' * (width-2)}╯")
            return "\n".join(output)
        
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.visible_themes, len(self.themes))
        
        for idx, theme_name in enumerate(self.themes[start_idx:end_idx], start=start_idx + 1):
            if idx - 1 == self.selected_index:
                prefix = self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('highlight')))("│ ► ")
            else:
                prefix = "│   "
            
            theme_display = theme_name
            if theme_name == self.current_theme:
                theme_display += self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('success')))(" (current)")
            
            theme_colors = self.theme_service.themes[theme_name]
            preview = []

            output.append(f"{prefix}{self.terminal.color_rgb(*self._hex_to_rgb(theme_colors['title']))(theme_display)}".ljust(width+20) + "│")
            preview.append(self.terminal.color_rgb(*self._hex_to_rgb(theme_colors['subreddit']))(f"r/subreddit"))
            preview.append(self.terminal.color_rgb(*self._hex_to_rgb(theme_colors['author']))(f"u/author"))
            preview.append(self.terminal.color_rgb(*self._hex_to_rgb(theme_colors['score']))(f"↑100"))
            preview.append(self.terminal.color_rgb(*self._hex_to_rgb(theme_colors['comments']))(f"💬50"))
            text_color = theme_colors.get('text', theme_colors.get('content', '#ffffff'))
            preview.append(self.terminal.color_rgb(*self._hex_to_rgb(text_color))(f"This is a preview of the theme"))
            
            preview_line = "│    " + " | ".join(preview)
            output.append(f"{preview_line.ljust(width+97)}│")
            
            if idx < end_idx:
                output.append(f"├{'─' * (width-2)}┤")
            else:
                output.append(f"╰{'─' * (width-2)}╯")
        
        output.append(f"")
        
        output.append(f"╭{'─' * (width-2)}╮")
        output.append(f"│{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('Instructions:').center(width+21)}│")
        output.append(f"│    {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('text')))('• Up/Down Arrow: Navigate themes')}".ljust(width+24) + "│")
        output.append(f"│    {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('text')))('• Enter: Select theme')}".ljust(width+24) + "│")
        output.append(f"│    {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('text')))('• Escape: Return to settings')}".ljust(width+24) + "│")
        output.append(f"╰{'─' * (width-2)}╯")
        
        return "\n".join(output)

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

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