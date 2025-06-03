from blessed import Terminal
from services.theme_service import ThemeService
from utils.logger import Logger

class CommentInputView:
    def __init__(self, terminal):
        self.terminal = terminal
        self.theme_service = ThemeService()
        self.logger = Logger()
        self.comment_text = ""
        self.cursor_pos = 0
        self.current_post = None
        self.reddit_instance = None
        self.width = self.terminal.width - 24

    def display(self):
        width = self.terminal.width - 23 - 1
        output = []
        
        output.append(f"┬{'─' * (width-2)}┬")
        output.append(f"│{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('Add Comment').center(width+21)}│")
        output.append(f"├{'─' * (width-2)}┤")
        
        if self.current_post:
            output.append(f"│{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('title')))(f'Replying to: {self.current_post.title}')}{' ' * (width - len(self.current_post.title) - 12)}│")
            output.append(f"├{'─' * (width-2)}┤")
        
        # Comment input area
        comment_lines = self.comment_text.split('\n')
        for i, line in enumerate(comment_lines):
            while len(line) > width - 6:
                display_line = f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(line[:width-6])}"
                display_line += ' ' * (width - len(display_line) + 24) + "│"
                output.append(display_line)
                line = line[width-6:]
            
            if i == len(comment_lines) - 1:
                display_line = f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(line[:self.cursor_pos])}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('highlight')))('|')}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(line[self.cursor_pos:])}"
            else:
                display_line = f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(line)}"
            display_line += ' ' * (width - len(display_line) + 72) + "│"
            output.append(display_line)
        
        output.append(f"├{'─' * (width-2)}┤")
        output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('info')))('Instructions:')}{' ' * (width - 16)}│")
        output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• Type your comment')}{' ' * (width - 22)}│")
        output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• Enter to submit')}{' ' * (width - 20)}│")
        output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• Esc to cancel')}{' ' * (width - 18)}│")
        output.append(f"╰{'─' * (width-2)}╯")
        
        return "\n".join(output)

    def handle_input(self, key):
        if key == '\x1b':  # Escape
            return "cancel"
        elif key == '\r' or key == '\n':  # Enter
            if self.comment_text.strip():
                try:
                    self.current_post.reply(self.comment_text)
                    self.logger.info("Comment submitted successfully")
                    return "submitted"
                except Exception as e:
                    self.logger.error(f"Error submitting comment: {e}")
                    return f"error:{str(e)}"
            return "cancel"
        elif key == '\x7f' or key == '\x08':  # Backspace (both ASCII and ANSI)
            if self.cursor_pos > 0:
                self.comment_text = self.comment_text[:self.cursor_pos-1] + self.comment_text[self.cursor_pos:]
                self.cursor_pos -= 1
        elif len(key) == 1 and key.isprintable():
            self.comment_text = self.comment_text[:self.cursor_pos] + key + self.comment_text[self.cursor_pos:]
            self.cursor_pos += 1
        return None

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def set_post(self, post):
        self.current_post = post
        self.comment_text = ""
        self.cursor_pos = 0 