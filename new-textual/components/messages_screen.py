from textual.containers import Container, Vertical, ScrollableContainer
from textual.widgets import Static, Button, Input, TextArea
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

    def compose(self):
        with Vertical():
            yield Static("Messages", classes="title")
            yield Button("Compose New Message", id="compose_button")
            yield ScrollableContainer(id="messages_container")

    async def on_mount(self):
        self.logger.info("MessagesScreen on_mount called (start)")
        await self.load_messages()
        self.logger.info("MessagesScreen on_mount finished")

    async def load_messages(self):
        try:
            self.logger.info("load_messages called (start)")
            messages_container = self.query_one("#messages_container")
            messages_container.remove_children()
            self.logger.info("messages_container.remove_children() done")
            self.messages = self.reddit_service.get_messages()
            self.logger.info(f"Fetched {len(self.messages)} messages")
            if not self.messages:
                await messages_container.mount(Static("No messages found", classes="message-body", markup=False))
            for message in self.messages:
                msg_box = Container(
                    Static(f"From: {message.author}", classes="message-header"),
                    Static(f"Subject: {message.subject}", classes="message-header"),
                    Static(f"Date: {datetime.fromtimestamp(message.created_utc).strftime('%Y-%m-%d %H:%M:%S')}", classes="message-header"),
                    Static(message.body, classes="message-body", markup=False),
                    Container(
                        Button("Mark as Read" if message.new else "Mark as Unread", id=f"mark_{message.id}"),
                        Button("Reply", id=f"reply_{message.id}")
                    ),
                    classes="message"
                )
                await messages_container.mount(msg_box)
            self.logger.info("load_messages finished")
        except Exception as e:
            self.logger.error(f"Error loading messages: {str(e)}", exc_info=True)
            self.notify("Error loading messages", severity="error")

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "compose_button":
            await self.show_compose_form()
        elif event.button.id.startswith("mark_"):
            message_id = event.button.id.split("_")[1]
            message = next((m for m in self.messages if m.id == message_id), None)
            if message:
                if message.new:
                    self.reddit_service.mark_message_read(message)
                else:
                    self.reddit_service.mark_message_unread(message)
                await self.load_messages()
        elif event.button.id.startswith("reply_"):
            message_id = event.button.id.split("_")[1]
            message = next((m for m in self.messages if m.id == message_id), None)
            if message:
                await self.show_reply_form(message)
        elif event.button.id == "send_button":
            if self.reply_message:
                subject_input = self.query_one("#subject_input", Input)
                message_input = self.query_one("#message_input", TextArea)
                if subject_input and message_input:
                    if self.reddit_service.send_message(
                        self.reply_message.author,
                        subject_input.value,
                        message_input.value
                    ):
                        self.notify("Reply sent successfully!", severity="success")
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
                        message_input.value
                    ):
                        self.notify("Message sent successfully!", severity="success")
                        await self.load_messages()
                    else:
                        self.notify("Failed to send message", severity="error")
        elif event.button.id == "cancel_button":
            self.reply_message = None
            await self.load_messages()

    async def show_compose_form(self):
        messages_container = self.query_one("#messages_container")
        messages_container.remove_children()
        form = Container(
            Static("Compose New Message", classes="title"),
            Input(placeholder="To:", id="to_input"),
            Input(placeholder="Subject:", id="subject_input"),
            TextArea(id="message_input"),
            Button("Send", id="send_button"),
            Button("Cancel", id="cancel_button"),
            classes="compose-form"
        )
        await messages_container.mount(form)

    async def show_reply_form(self, original_message):
        self.reply_message = original_message
        messages_container = self.query_one("#messages_container")
        messages_container.remove_children()
        form = Container(
            Static(f"Reply to {original_message.author}", classes="title"),
            Input(value=f"Re: {original_message.subject}", id="subject_input"),
            TextArea(id="message_input"),
            Button("Send", id="send_button"),
            Button("Cancel", id="cancel_button"),
            classes="compose-form"
        )
        await messages_container.mount(form)

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "to_input":
            self.query_one("#subject_input").focus()
        elif event.input.id == "subject_input":
            self.query_one("#message_input").focus() 