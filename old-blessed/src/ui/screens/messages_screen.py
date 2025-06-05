from blessed import Terminal
import datetime
import time
from services.theme_service import ThemeService
from services.settings_service import Settings
from utils.logger import Logger
import praw

class MessagesScreen:
    def __init__(self, terminal, reddit_instance):
        self.terminal = terminal
        self.reddit_instance = reddit_instance
        self.theme_service = ThemeService()
        self.settings = Settings()
        self.settings.load_settings_from_file()
        self.logger = Logger()
        self.selected_index = 0
        self.scroll_offset = 0
        self.visible_messages = 15
        self.messages = []
        self.is_loading = False
        self.loading_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.loading_index = 0
        self.last_loading_update = 0
        self.width = self.terminal.width - 24
        self.compose_mode = False
        self.recipient = ""
        self.subject = ""
        self.message_text = ""
        self.cursor_pos = 0
        self.current_field = "recipient"
        self.active = False
        self.reply_to_message = None

    def display(self):
        width = self.terminal.width - 23 - 1
        output = []
        
        if self.compose_mode:
            output.append(f"┬{'─' * (width-2)}┬")
            output.append(f"│{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('Compose Message').center(width+21)}│")
            output.append(f"├{'─' * (width-2)}┤")

            output.append(f"│{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('I currently do not know if this is the right use of PRAW direct messages (doesnt seem to be). So this function is currently unsupported.').center(width+21)}│")
            output.append(f"├{'─' * (width-2)}┤")
            output.append(f"│{self.terminal.red('UNSUPPORTED & BUGGY | USE WITH CAUTION').center(width+9)}│")
            output.append(f"├{'─' * (width-2)}┤")
            
            if hasattr(self, 'reply_to_message') and self.reply_to_message:
                messages = []
                if isinstance(self.reply_to_message, praw.models.Message):
                    messages = list(self.reddit_instance.inbox.messages(limit=50))
                    messages = [msg for msg in messages if (msg.author and msg.author.name == self.recipient) or 
                              (hasattr(msg, 'dest') and msg.dest.name == self.recipient)]
                elif isinstance(self.reply_to_message, praw.models.Comment):
                    messages = list(self.reddit_instance.inbox.comment_replies(limit=50))
                    messages = [msg for msg in messages if (msg.author and msg.author.name == self.recipient) or 
                              (hasattr(msg, 'parent_id') and msg.parent_id == self.reply_to_message.id)]
                
                for msg in reversed(messages):
                    if isinstance(msg, praw.models.Message):
                        body = msg.body
                        author = msg.author.name if hasattr(msg, 'author') and msg.author else "Unknown"
                        is_sent = author != self.reddit_instance.user.me().name
                    else:
                        body = msg.body
                        author = msg.author.name if hasattr(msg, 'author') and msg.author else "Unknown"
                        is_sent = author != self.reddit_instance.user.me().name
                    
                    timestamp = datetime.datetime.fromtimestamp(msg.created_utc).strftime('%H:%M')
                    author_display = f"{author} • {timestamp}"
                    
                    wrapped_lines = []
                    current_line = ""
                    for word in body.split():
                        if len(current_line) + len(word) + 1 <= width - 8:
                            current_line += (word + " ")
                        else:
                            wrapped_lines.append(current_line.strip())
                            current_line = word + " "
                    if current_line:
                        wrapped_lines.append(current_line.strip())
                    
                    if is_sent:
                        output.append(f"│{' ' * (width-2)}│")
                        output.append(f"│{' ' * (width-2)}│")
                        for line in wrapped_lines:
                            padding = width - len(line) - 6
                            output.append(f"│{' ' * padding}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(line)}{' ' * 6}│")
                        author_padding = width - len(author_display) - 6
                        output.append(f"│{' ' * author_padding}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('subreddit')))(author_display)}{' ' * 6}│")
                    else:
                        output.append(f"│{' ' * (width-2)}│")
                        output.append(f"│{' ' * (width-2)}│")
                        for line in wrapped_lines:
                            output.append(f"│{' ' * 6}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(line)}{' ' * (width - len(line) - 6)}│")
                        output.append(f"│{' ' * 6}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('subreddit')))(author_display)}{' ' * (width - len(author_display) - 6)}│")
                
                output.append(f"├{'─' * (width-2)}┤")
            
            recipient_line = f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('To: ')}"
            if self.current_field == "recipient":
                recipient_line += f"{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(self.recipient[:self.cursor_pos])}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('highlight')))('|')}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(self.recipient[self.cursor_pos:])}"
            else:
                recipient_line += self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(self.recipient)
            recipient_line += ' ' * (width - len(recipient_line) + 47) + "│"
            output.append(recipient_line)
            
            subject_line = f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('Subject: ')}"
            if self.current_field == "subject":
                subject_line += f"{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(self.subject[:self.cursor_pos])}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('highlight')))('|')}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(self.subject[self.cursor_pos:])}"
            else:
                subject_line += self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(self.subject)
            subject_line += ' ' * (width - len(subject_line) + 47) + "│"
            output.append(subject_line)
            
            output.append(f"├{'─' * (width-2)}┤")
            
            message_lines = self.message_text.split('\n')
            for i, line in enumerate(message_lines):
                while len(line) > width - 6:
                    display_line = f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(line[:width-6])}"
                    display_line += ' ' * (width - len(display_line) + 24) + "│"
                    output.append(display_line)
                    line = line[width-6:]
                
                if self.current_field == "message" and i == len(message_lines) - 1:
                    display_line = f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(line[:self.cursor_pos])}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('highlight')))('|')}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(line[self.cursor_pos:])}"
                else:
                    display_line = f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(line)}"
                display_line += ' ' * (width - len(display_line) + 72) + "│"
                output.append(display_line)
            
            output.append(f"├{'─' * (width-2)}┤")
            output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('info')))('Instructions:')}{' ' * (width - 16)}│")
            output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• Tab to switch fields')}{' ' * (width - 25)}│")
            output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• Enter to send')}{' ' * (width - 18)}│")
            output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• Esc to cancel')}{' ' * (width - 18)}│")
            output.append(f"╰{'─' * (width-2)}╯")
            return "\n".join(output)
        
        output.append(f"┬{'─' * (width-2)}┤")
        output.append(f"│{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('Direct Messages').center(width+21)}│")
        output.append(f"├{'─' * (width-2)}┤")

        output.append(f"│{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('panel_title')))('I currently do not know if this is the right use of PRAW direct messages (doesnt seem to be). So this function is currently unsupported.').center(width+21)}│")
        output.append(f"├{'─' * (width-2)}┤")
        output.append(f"│{self.terminal.red('UNSUPPORTED & BUGGY | USE WITH CAUTION').center(width+9)}│")
        output.append(f"├{'─' * (width-2)}┤")
        
        if self.messages:
            start_idx = self.scroll_offset
            end_idx = min(start_idx + self.visible_messages, len(self.messages))
            
            for idx, message in enumerate(self.messages[start_idx:end_idx], start=start_idx + 1):
                if idx - 1 == self.selected_index and self.active:
                    prefix = self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('highlight')))("► ")
                else:
                    prefix = "  "
                
                item_num = f"{idx}."
                
                if isinstance(message, praw.models.Message):
                    subject = message.subject if hasattr(message, 'subject') else "No subject"
                    author = message.author.name if hasattr(message, 'author') and message.author else "Unknown"
                    created = datetime.datetime.fromtimestamp(message.created_utc).strftime('%Y-%m-%d')
                    is_read = not hasattr(message, 'new') or not message.new
                elif isinstance(message, praw.models.Comment):
                    subject = message.body.replace('\n', ' ')[:50] + "..." if len(message.body) > 50 else message.body.replace('\n', ' ')
                    author = message.author.name if hasattr(message, 'author') and message.author else "Unknown"
                    created = datetime.datetime.fromtimestamp(message.created_utc).strftime('%Y-%m-%d')
                    is_read = not hasattr(message, 'new') or not message.new
                else:
                    subject = str(message).replace('\n', ' ')
                    author = "Unknown"
                    created = datetime.datetime.now().strftime('%Y-%m-%d')
                    is_read = True
                
                if len(subject) > width - 40:
                    subject = subject[:width-43] + "..."
                
                item_line = f"{prefix}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('title')))(item_num)} {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(subject)}"
                metadata = f" | From: {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('subreddit')))(author)} | {created}"
                
                metadata_additional_width = 0
                if not is_read:
                    metadata += f" | {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('highlight')))('NEW')}"
                    metadata_additional_width += 23
                
                full_line = item_line + metadata
                if len(full_line) > width - 6:
                    available_space = width - 6 - len(metadata)
                    item_line = f"{prefix}{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('title')))(item_num)} {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))(subject[:available_space-3])}..."
                    full_line = item_line + metadata

                if prefix == "  ":
                    output.append(f"│ {full_line}{' ' * (width - len(full_line) + 66 + metadata_additional_width)}│")
                else:
                    output.append(f"│ {full_line}{' ' * (width - len(full_line) + 89 + metadata_additional_width)}│")
                if idx < end_idx:
                    output.append(f"├{'─' * (width-2)}┤")
        else:
            if self.is_loading:
                output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('warning')))('Loading messages...')}{' ' * (width - 19)}│")
            else:
                output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('warning')))('No messages found.')}{' ' * (width - 20)}│")
        
        output.append(f"├{'─' * (width-2)}┤")
        output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('info')))('Instructions:')}{' ' * (width - 16)}│")
        output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• Up/Down to navigate')}{' ' * (width - 24)}│")
        output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• Enter to view message')}{' ' * (width - 26)}│")
        output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• N to compose new message')}{' ' * (width - 29)}│")
        output.append(f"│ {self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('content')))('• Esc to return')}{' ' * (width - 18)}│")
        output.append(f"╰{'─' * (width-2)}╯")
        
        if self.is_loading:
            current_time = time.time()
            refresh_rate = float(self.settings.get_setting('spinner_refresh_rate')) / 1000  # Convert ms to seconds
            if current_time - self.last_loading_update >= refresh_rate:
                self.loading_index = (self.loading_index + 1) % len(self.loading_chars)
                self.last_loading_update = current_time
            loading_text = f"{self.terminal.color_rgb(*self._hex_to_rgb(self.theme_service.get_style('info')))(self.loading_chars[self.loading_index])} Loading..."
            print(self.terminal.move(self.terminal.height - 1, 0) + loading_text)
        
        return "\n".join(output)

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def load_messages(self):
        if not self.reddit_instance:
            self.logger.warning("Attempted to load messages without Reddit instance")
            return
        
        self.is_loading = True
        try:
            self.messages = list(self.reddit_instance.inbox.all(limit=self.settings.get_setting('posts_per_page')))
            self.selected_index = 0
            self.scroll_offset = 0
            self.logger.info(f"Loaded {len(self.messages)} messages")
        except Exception as e:
            error_msg = f"Error loading messages: {str(e)}"
            self.terminal.print_at(0, 0, error_msg, self.theme_service.get_style("error"))
            self.logger.error(error_msg, exc_info=True)
        finally:
            self.is_loading = False

    def scroll_up(self):
        if self.scroll_offset > 0:
            self.scroll_offset = max(0, self.scroll_offset - 3)
            self.logger.debug(f"Scrolled up in messages. New offset: {self.scroll_offset}")

    def scroll_down(self):
        if self.scroll_offset < len(self.messages) - self.visible_messages:
            self.scroll_offset = min(len(self.messages) - self.visible_messages, self.scroll_offset + 3)
            self.logger.debug(f"Scrolled down in messages. New offset: {self.scroll_offset}")

    def select_message(self):
        if not self.messages:
            self.logger.debug("Attempted to select message but no messages available")
            return None
        selected_message = self.messages[self.scroll_offset + self.selected_index]
        if hasattr(selected_message, 'mark_read'):
            selected_message.mark_read()
            self.logger.debug(f"Marked message as read: {selected_message.id}")
        return selected_message

    def send_message(self):
        if not self.recipient or not self.subject or not self.message_text:
            self.logger.warning("Attempted to send message with missing fields")
            return False
        
        try:
            self.logger.info(f"Attempting to send message to {self.recipient}")
            self.reddit_instance.redditor(self.recipient).message(self.subject, self.message_text)
            self.logger.info(f"Message sent to {self.recipient}")
            self.compose_mode = False
            self.recipient = ""
            self.subject = ""
            self.message_text = ""
            self.cursor_pos = 0
            self.current_field = "recipient"
            self.load_messages()
            return True
        except Exception as e:
            error_msg = f"Error sending message: {str(e)}"
            print(error_msg)
            self.logger.error(error_msg, exc_info=True)
            return False

    def start_compose(self):
        self.logger.info("Starting new message composition")
        self.compose_mode = True
        self.recipient = ""
        self.subject = ""
        self.message_text = ""
        self.cursor_pos = 0
        self.current_field = "recipient"

    def start_reply(self, message):
        self.logger.info(f"Starting reply to message from {message.author.name if hasattr(message, 'author') else 'Unknown'}")
        self.compose_mode = True
        self.reply_to_message = message
        if hasattr(message, 'author'):
            self.recipient = message.author.name
        if hasattr(message, 'subject'):
            self.subject = f"Re: {message.subject}"
        else:
            self.subject = "Re: Message"
        self.message_text = ""
        self.cursor_pos = 0
        self.current_field = "message"

    def next_message(self):
        if self.selected_index < min(self.visible_messages - 1, len(self.messages) - self.scroll_offset - 1):
            self.selected_index += 1
            if self.scroll_offset < len(self.messages) - self.visible_messages:
                self.scroll_down()
            self.logger.debug(f"Selected next message. New index: {self.selected_index}")

    def previous_message(self):
        if self.selected_index > 0:
            self.selected_index -= 1
            if self.scroll_offset > 0:
                self.scroll_up()
            self.logger.debug(f"Selected previous message. New index: {self.selected_index}") 