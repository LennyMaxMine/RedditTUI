from textual.widget import Widget
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Static, Button, Input
from textual.events import Click
from textual.message import Message
from textual.reactive import reactive
from rich.text import Text
from datetime import datetime
from utils.logger import Logger
from components.sidebar import Sidebar

class AccountList(Widget):
    selected_index = reactive(0)

    def __init__(self, reddit_service, **kwargs):
        super().__init__(**kwargs)
        self.reddit_service = reddit_service
        self.logger = Logger()
        self.accounts = []
        self.can_focus = True

    def on_mount(self):
        self.logger.info("AccountList mounted")
        self.load_accounts()

    def load_accounts(self):
        self.accounts = self.reddit_service.get_accounts()
        self.logger.info(f"Loaded {len(self.accounts)} accounts")
        self.refresh()

    def render(self) -> Text:
        if not self.accounts:
            return Text("No accounts found. Add your first account!", justify="center")

        current_account = self.reddit_service.get_current_account()
        
        lines = []
        for i, username in enumerate(self.accounts):
            account_data = self.reddit_service.accounts.get(username, {})
            added_date = datetime.fromtimestamp(account_data.get("added_date", 0)).strftime("%Y-%m-%d")
            last_used = datetime.fromtimestamp(account_data.get("last_used", 0)).strftime("%Y-%m-%d %H:%M")

            is_current = username == current_account
            is_selected = i == self.selected_index

            status_text = " (Current)" if is_current else ""
            cursor = "▶ " if is_selected else "  "
            
            line = Text()
            
            base_style = "bold green" if is_current else "white"
            style = base_style
            if is_selected:
                style += " on #1F2937" 

            line.append(cursor, style)
            line.append(f"{username}{status_text}\n", style)
            line.append(f"  Added: {added_date}\n", "dim")
            line.append(f"  Last used: {last_used}\n\n", "dim")
            lines.append(line)

        return Text.assemble(*lines)

    def on_key(self, event):
        if event.key == "up":
            self.selected_index = max(0, self.selected_index - 1)
            event.prevent_default()
        elif event.key == "down":
            self.selected_index = min(len(self.accounts) - 1, self.selected_index + 1)
            event.prevent_default()
        elif event.key == "enter":
            if 0 <= self.selected_index < len(self.accounts):
                self.post_message(self.AccountSelected(self.accounts[self.selected_index]))
            event.stop()
        
        return event

    def get_selected_account(self):
        if 0 <= self.selected_index < len(self.accounts):
            return self.accounts[self.selected_index]
        return None

    class AccountSelected(Message):
        def __init__(self, username):
            super().__init__()
            self.username = username

class AddAccountForm(Widget):
    def __init__(self, reddit_service, **kwargs):
        super().__init__(**kwargs)
        self.reddit_service = reddit_service
        self.logger = Logger()

    def compose(self):
        with Vertical(classes="add_account_form"):
            yield Static("Add New Account", classes="section_title")
            yield Input(placeholder="Username", id="username_input")
            yield Input(placeholder="Client ID", id="client_id_input")
            yield Input(placeholder="Client Secret", id="client_secret_input")
            yield Input(placeholder="Password", id="password_input", password=True)
            
            with Horizontal(id="add_account_actions"):
                yield Button("Add", id="confirm_add_button")
                yield Button("Cancel", id="cancel_add_button")

    def on_mount(self):
        self.logger.info("AddAccountForm mounted")
        self.query_one("#username_input").focus()

    def on_button_pressed(self, event: Button.Pressed):
        button_id = event.button.id
        
        if button_id == "confirm_add_button":
            self.add_account()
        elif button_id == "cancel_add_button":
            self.post_message(self.Cancelled())

    def add_account(self):
        username_input = self.query_one("#username_input", Input)
        client_id_input = self.query_one("#client_id_input", Input)
        client_secret_input = self.query_one("#client_secret_input", Input)
        password_input = self.query_one("#password_input", Input)
        
        username = username_input.value.strip()
        client_id = client_id_input.value.strip()
        client_secret = client_secret_input.value.strip()
        password = password_input.value.strip()
        
        if not all([username, client_id, client_secret, password]):
            self.notify("Please fill in all fields", severity="warning")
            return
        
        if self.reddit_service.add_account(username, client_id, client_secret, password):
            self.notify(f"Account {username} added successfully", severity="information")
            self.post_message(self.AccountAdded(username))
            self.clear_form()
        else:
            self.notify(f"Failed to add account {username}", severity="error")

    def clear_form(self):
        username_input = self.query_one("#username_input", Input)
        client_id_input = self.query_one("#client_id_input", Input)
        client_secret_input = self.query_one("#client_secret_input", Input)
        password_input = self.query_one("#password_input", Input)
        
        username_input.value = ""
        client_id_input.value = ""
        client_secret_input.value = ""
        password_input.value = ""

    class AccountAdded(Message):
        def __init__(self, username):
            super().__init__()
            self.username = username

    class Cancelled(Message):
        pass

class AccountManagementWidget(Vertical):
    def __init__(self, reddit_service, **kwargs):
        super().__init__(id="account_management_widget", **kwargs)
        self.reddit_service = reddit_service
        self.logger = Logger()

    def compose(self):
        yield Static("Account Management", classes="title")
        yield ScrollableContainer(id="view_container")
        with Horizontal(id="account_actions"):
            yield Button("Add Account", id="add_account_button")
            yield Button("Remove Account", id="remove_account_button")
            yield Button("Switch Account", id="switch_account_button")
            yield Button("Back to Posts", id="back_button")

    def on_mount(self):
        self.logger.info("AccountManagementWidget mounted")
        self.show_account_list()

    def show_account_list(self):
        container = self.query_one("#view_container", ScrollableContainer)
        container.remove_children()
        account_list = AccountList(self.reddit_service, id="account_list")
        container.mount(account_list)
        account_list.focus()
        self.query_one("#account_actions").display = True

    def show_add_account_form(self):
        container = self.query_one("#view_container", ScrollableContainer)
        container.remove_children()
        add_form = AddAccountForm(self.reddit_service, id="add_account_form")
        container.mount(add_form)
        add_form.focus()
        self.query_one("#account_actions").display = False

    def on_button_pressed(self, event: Button.Pressed):
        button_id = event.button.id
        
        if button_id == "add_account_button":
            self.show_add_account_form()
        elif button_id == "remove_account_button":
            self.remove_selected_account()
        elif button_id == "switch_account_button":
            self.switch_selected_account()
        elif button_id == "back_button":
            self.post_message(self.BackRequested())

    def remove_selected_account(self):
        try:
            account_list = self.query_one("#account_list", AccountList)
            selected_account = account_list.get_selected_account()
            
            if not selected_account:
                self.notify("No account selected", severity="warning")
                return
            
            if selected_account == self.reddit_service.get_current_account():
                self.notify("Cannot remove the currently active account", severity="warning")
                return
            
            if self.reddit_service.remove_account(selected_account):
                self.notify(f"Account {selected_account} removed successfully", severity="information")
                account_list.load_accounts()
            else:
                self.notify(f"Failed to remove account {selected_account}", severity="error")
        except Exception:
            self.notify("Not in account list view. (Error)", severity="error")

    def switch_selected_account(self):
        try:
            account_list = self.query_one("#account_list", AccountList)
            selected_account = account_list.get_selected_account()
            
            if not selected_account:
                self.notify("No account selected", severity="warning")
                return
            
            self.switch_to_account(selected_account)
        except Exception:
            self.notify("Not in account list view. (Error)", severity="error")

    def switch_to_account(self, username):
        self.logger.info(f"Switching to account: {username}")
        if self.reddit_service.switch_account(username):
            current_account = self.reddit_service.get_current_account()
            if current_account:
                sidebar = self.app.query_one(Sidebar)
                sidebar.update_sidebar_account(current_account)
            self.notify(f"Switched to account: {username}", severity="information")
            self.post_message(self.AccountSwitched(username))
        else:
            self.notify(f"Failed to switch to account: {username}", severity="error")

    def on_account_list_account_selected(self, message: AccountList.AccountSelected):
        self.switch_to_account(message.username)

    def on_add_account_form_account_added(self, message: AddAccountForm.AccountAdded):
        self.show_account_list()

    def on_add_account_form_cancelled(self, message: AddAccountForm.Cancelled):
        self.show_account_list()

    class AccountSwitched(Message):
        def __init__(self, username):
            super().__init__()
            self.username = username

    class BackRequested(Message):
        pass 