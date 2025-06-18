from textual.containers import Container, Vertical, ScrollableContainer, Horizontal
from textual.widgets import Static, Button, Input, TextArea, Select
from textual.events import Click
from datetime import datetime
from utils.logger import Logger

class MessagesScreen(Container):
    def __init__(self, reddit_service):
        super().__init__()
        self.reddit_service = reddit_service
        self.messages = []
        self.logger = Logger()
        self.compose_mode = False
        self.reply_message = None
        self.search_query = ""
        self.sort_by = "date"
        self.filter_status = "all"
        self.selected_conversation = None
        self.selected_index = 0
        self.conversations = []

    def compose(self):
        with Horizontal():
            with Vertical(id="conversations_panel"):
                yield Static("Conversations", classes="title")
                with Horizontal():
                    yield Input(placeholder="Search conversations...", id="search_input")
                    yield Select(
                        [(v, k) for k, v in {
                            "date": "Date",
                            "author": "Author",
                            "subject": "Subject"
                        }.items()],
                        id="sort_select"
                    )
                    yield Select(
                        [(v, k) for k, v in {
                            "all": "All",
                            "unread": "Unread",
                            "read": "Read"
                        }.items()],
                        id="filter_select"
                    )
                yield Button("Compose New Message", id="compose_button")
                yield Button("Refresh", id="refresh_button")
                yield Button("Mark All Read", id="mark_all_read_button")
                with ScrollableContainer(id="conversations_list"):
                    yield Static("Loading conversations...", id="conversations_placeholder")
            with Vertical(id="messages_panel"):
                yield Static("Messages", classes="title", id="messages_title")
                yield Button("Back to Conversations", id="back_button")
                yield Button("Refresh Messages", id="refresh_messages_button")
                yield ScrollableContainer(id="messages_container")

    async def on_mount(self):
        self.logger.info("MessagesScreen on_mount called (start)")
        await self.load_messages()
        self.logger.info("MessagesScreen on_mount finished")

    def _truncate_text(self, text, max_length=50):
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."

    def _format_time(self, timestamp):
        now = datetime.now()
        message_time = datetime.fromtimestamp(timestamp)
        time_diff = now - message_time
        
        if time_diff.days > 0:
            return message_time.strftime('%Y-%m-%d')
        elif time_diff.seconds > 3600:
            hours = time_diff.seconds // 3600
            return f"{hours}h ago"
        elif time_diff.seconds > 60:
            minutes = time_diff.seconds // 60
            return f"{minutes}m ago"
        else:
            return "Just now"

    async def load_messages(self):
        try:
            self.logger.info("load_messages called (start)")
            conversations_list = self.query_one("#conversations_list")
            conversations_list.remove_children()
            self.logger.info("conversations_list.remove_children() done")
            self.messages = self.reddit_service.get_messages()
            self.logger.info(f"Fetched {len(self.messages)} messages")
            
            filtered_messages = self._filter_messages(self.messages)
            sorted_messages = self._sort_messages(filtered_messages)
            
            if not sorted_messages:
                await conversations_list.mount(Static("No messages found", classes="message-body", markup=False))
                return
            
            conversations = {}
            for message in sorted_messages:
                author = str(message.author)
                if author not in conversations:
                    conversations[author] = []
                conversations[author].append(message)
            
            self.conversations = []
            for author, messages in conversations.items():
                if self.search_query and self.search_query.lower() not in author.lower():
                    continue
                    
                latest_message = max(messages, key=lambda x: x.created_utc)
                unread_count = sum(1 for m in messages if m.new)
                
                subject_text = self._truncate_text(str(latest_message.subject), 40)
                time_text = self._format_time(latest_message.created_utc)
                
                conversation_box = Container(
                    Static(str(author), classes="conversation-name"),
                    Static(subject_text, classes="conversation-preview"),
                    Static(time_text, classes="conversation-time"),
                    Static(f"{unread_count} unread" if unread_count > 0 else "", classes="unread-badge"),
                    classes=f"conversation {'unread' if unread_count > 0 else ''} {'selected' if author == self.selected_conversation else ''}",
                    id=f"conv_{author}"
                )
                self.conversations.append((author, conversation_box))
                await conversations_list.mount(conversation_box)
            
            if self.conversations:
                if self.selected_conversation and any(author == self.selected_conversation for author, _ in self.conversations):
                    await self.show_conversation(self.selected_conversation)
                else:
                    self.selected_index = 0
                    self.selected_conversation = self.conversations[0][0]
                    self._update_selection()
                    await self.show_conversation(self.selected_conversation)
            else:
                self.query_one("#messages_title", Static).update("No conversations found")
                self.query_one("#messages_container").remove_children()
                await self.query_one("#messages_container").mount(Static("No conversations match your search criteria", classes="message-body", markup=False))
            
            self.logger.info("load_messages finished")
        except Exception as e:
            self.logger.error(f"Error loading messages: {str(e)}", exc_info=True)
            self.notify("Error loading messages", severity="error")

    def on_key(self, event):
        if not self.conversations:
            return event

        if event.key == "up":
            self.selected_index = max(0, self.selected_index - 1)
            self._update_selection()
            event.prevent_default()
        elif event.key == "down":
            self.selected_index = min(len(self.conversations) - 1, self.selected_index + 1)
            self._update_selection()
            event.prevent_default()
        elif event.key == "enter":
            if 0 <= self.selected_index < len(self.conversations):
                author = self.conversations[self.selected_index][0]
                self.selected_conversation = author
                self._update_selection()
                self.call_later(self.show_conversation, author)
                event.prevent_default()

        return event

    def _update_selection(self):
        for i, (author, box) in enumerate(self.conversations):
            if i == self.selected_index:
                box.add_class("selected")
                self.selected_conversation = author
            else:
                box.remove_class("selected")

    def _filter_messages(self, messages):
        if self.filter_status == "all":
            return messages
        return [m for m in messages if (self.filter_status == "unread" and m.new) or (self.filter_status == "read" and not m.new)]

    def _sort_messages(self, messages):
        if self.sort_by == "date":
            return sorted(messages, key=lambda x: x.created_utc, reverse=True)
        elif self.sort_by == "author":
            return sorted(messages, key=lambda x: x.author)
        elif self.sort_by == "subject":
            return sorted(messages, key=lambda x: x.subject)
        return messages

    async def on_input_changed(self, event: Input.Changed):
        if event.input.id == "search_input":
            self.search_query = event.value.lower()
            await self.load_messages()

    async def on_select_changed(self, event: Select.Changed):
        if event.select.id == "sort_select":
            self.sort_by = event.value
            await self.load_messages()
        elif event.select.id == "filter_select":
            self.filter_status = event.value
            await self.load_messages()

    async def on_click(self, event: Click):
        control = event.control
        while control and (not hasattr(control, 'id') or not control.id or not control.id.startswith("conv_")):
            control = control.parent
        
        if control and hasattr(control, 'id') and control.id and control.id.startswith("conv_"):
            author = control.id[5:]
            self.selected_conversation = author
            self.selected_index = next((i for i, (a, _) in enumerate(self.conversations) if a == author), 0)
            self._update_selection()
            await self.show_conversation(author)

    async def show_conversation(self, author):
        try:
            self.query_one("#messages_title", Static).update(f"Conversation with {author}")
            messages_container = self.query_one("#messages_container")
            messages_container.remove_children()
            
            conversation_messages = [m for m in self.messages if str(m.author) == author]
            conversation_messages.sort(key=lambda x: x.created_utc)
            
            if not conversation_messages:
                await messages_container.mount(Static("No messages in this conversation", classes="message-body", markup=False))
                return
            
            for message in conversation_messages:
                time_text = self._format_time(message.created_utc)
                status_text = " (Unread)" if message.new else ""
                
                msg_box = Container(
                    Container(
                        Static(f"From: {message.author}{status_text}", classes="message-header"),
                        Static(f"Subject: {message.subject}", classes="message-header"),
                        Static(f"Date: {time_text}", classes="message-header"),
                        classes="message-header-container"
                    ),
                    Static(message.body, classes="message-body", markup=False),
                    Container(
                        Button("Mark as Read" if message.new else "Mark as Unread", id=f"mark_{message.id}"),
                        Button("Reply", id=f"reply_{message.id}"),
                        Button("Delete", id=f"delete_{message.id}"),
                        classes="message-actions"
                    ),
                    classes=f"message {'unread' if message.new else 'read'}"
                )
                await messages_container.mount(msg_box)
        except Exception as e:
            self.logger.error(f"Error showing conversation: {str(e)}", exc_info=True)
            self.notify("Error loading conversation", severity="error")

    async def on_button_pressed(self, event: Button.Pressed):
        try:
            if event.button.id == "compose_button":
                await self.show_compose_form()
            elif event.button.id == "refresh_button":
                await self.load_messages()
                self.notify("Messages refreshed", severity="information")
            elif event.button.id == "mark_all_read_button":
                await self.mark_all_messages_read()
            elif event.button.id == "back_button":
                await self.show_conversations_list()
            elif event.button.id == "refresh_messages_button":
                if self.selected_conversation:
                    await self.show_conversation(self.selected_conversation)
                    self.notify("Messages refreshed", severity="information")
            elif event.button.id and event.button.id.startswith("mark_"):
                message_id = event.button.id.split("_")[1]
                message = next((m for m in self.messages if m.id == message_id), None)
                if message:
                    if message.new:
                        self.reddit_service.mark_message_read(message)
                    else:
                        self.reddit_service.mark_message_unread(message)
                    await self.load_messages()
            elif event.button.id and event.button.id.startswith("reply_"):
                message_id = event.button.id.split("_")[1]
                message = next((m for m in self.messages if m.id == message_id), None)
                if message:
                    await self.show_reply_form(message)
            elif event.button.id and event.button.id.startswith("delete_"):
                message_id = event.button.id.split("_")[1]
                message = next((m for m in self.messages if m.id == message_id), None)
                if message:
                    await self.delete_message(message)
            elif event.button.id == "send_button":
                if self.reply_message:
                    subject_input = self.query_one("#subject_input", Input)
                    message_input = self.query_one("#message_input", TextArea)
                    if subject_input and message_input:
                        if self.reddit_service.send_message(
                            self.reply_message.author,
                            subject_input.value,
                            message_input.text
                        ):
                            self.notify("Reply sent successfully!", severity="information")
                            self.reply_message = None
                            await self.load_messages()
                        else:
                            self.notify("Failed to send reply", severity="error")
                else:
                    to_input = self.query_one("#to_input", Input)
                    subject_input = self.query_one("#subject_input", Input)
                    message_input = self.query_one("#message_input", TextArea)
                    if to_input and subject_input and message_input:
                        if self.reddit_service.send_message(
                            to_input.value,
                            subject_input.value,
                            message_input.text
                        ):
                            self.notify("Message sent successfully!", severity="information")
                            await self.load_messages()
                        else:
                            self.notify("Failed to send message", severity="error")
            elif event.button.id == "cancel_button":
                self.reply_message = None
                await self.load_messages()
        except Exception as e:
            self.logger.error(f"Error handling button press: {str(e)}", exc_info=True)
            self.notify("Error processing action", severity="error")

    async def show_compose_form(self):
        try:
            messages_container = self.query_one("#messages_container")
            messages_container.remove_children()
            form = Container(
                Static("Compose New Message", classes="title"),
                Input(placeholder="To:", id="to_input"),
                Input(placeholder="Subject:", id="subject_input"),
                TextArea(id="message_input"),
                Container(
                    Button("Send", id="send_button"),
                    Button("Cancel", id="cancel_button"),
                    classes="button-container"
                ),
                classes="compose-form"
            )
            await messages_container.mount(form)
            self.query_one("#to_input").focus()
        except Exception as e:
            self.logger.error(f"Error showing compose form: {str(e)}", exc_info=True)
            self.notify("Error opening compose form", severity="error")

    async def show_reply_form(self, original_message):
        try:
            self.reply_message = original_message
            messages_container = self.query_one("#messages_container")
            messages_container.remove_children()
            form = Container(
                Static(f"Reply to {original_message.author}", classes="title"),
                Input(value=f"Re: {original_message.subject}", id="subject_input"),
                TextArea(id="message_input"),
                Container(
                    Button("Send", id="send_button"),
                    Button("Cancel", id="cancel_button"),
                    classes="button-container"
                ),
                classes="compose-form"
            )
            await messages_container.mount(form)
            self.query_one("#message_input").focus()
        except Exception as e:
            self.logger.error(f"Error showing reply form: {str(e)}", exc_info=True)
            self.notify("Error opening reply form", severity="error")

    def on_input_submitted(self, event: Input.Submitted):
        try:
            if event.input.id == "to_input":
                self.query_one("#subject_input").focus()
            elif event.input.id == "subject_input":
                self.query_one("#message_input").focus()
        except Exception as e:
            self.logger.error(f"Error handling input submission: {str(e)}", exc_info=True)

    async def mark_all_messages_read(self):
        try:
            unread_messages = [m for m in self.messages if m.new]
            if not unread_messages:
                self.notify("No unread messages to mark", severity="information")
                return
            
            marked_count = 0
            for message in unread_messages:
                if self.reddit_service.mark_message_read(message):
                    marked_count += 1
            
            if marked_count > 0:
                self.notify(f"Marked {marked_count} messages as read", severity="information")
                await self.load_messages()
            else:
                self.notify("Failed to mark messages as read", severity="error")
        except Exception as e:
            self.logger.error(f"Error marking all messages as read: {str(e)}", exc_info=True)
            self.notify("Error marking messages as read", severity="error")

    async def show_conversations_list(self):
        try:
            self.query_one("#messages_title", Static).update("Messages")
            messages_container = self.query_one("#messages_container")
            messages_container.remove_children()
            await messages_container.mount(Static("Select a conversation to view messages", classes="message-body", markup=False))
        except Exception as e:
            self.logger.error(f"Error showing conversations list: {str(e)}", exc_info=True)
            self.notify("Error showing conversations", severity="error")

    async def delete_message(self, message):
        try:
            if self.reddit_service.delete_message(message):
                self.notify("Message deleted successfully!", severity="information")
                await self.load_messages()
            else:
                self.notify("Failed to delete message", severity="error")
        except Exception as e:
            self.logger.error(f"Error deleting message: {str(e)}", exc_info=True)
            self.notify("Error deleting message", severity="error") 