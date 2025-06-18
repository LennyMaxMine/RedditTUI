from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Static, Button, Input, Select
from textual.screen import ModalScreen
from textual.events import Click
from datetime import datetime
from utils.logger import Logger

class AccountManagementScreen(ModalScreen):
    def __init__(self, reddit_service):
        super().__init__()
        self.reddit_service = reddit_service
        self.logger = Logger()
        self.accounts = []
        self.selected_index = 0
        self.mode = "list"

    def compose(self):
        with Container(id="account_container"):
            yield Static("Account Management", classes="title")
            
            with Vertical(id="account_list_container"):
                yield Static("Current Accounts:", classes="section_title")
                with ScrollableContainer(id="accounts_list"):
                    yield Static("Loading accounts...", id="accounts_placeholder")
                
                with Horizontal(id="account_actions"):
                    yield Button("Add Account", id="add_account_button")
                    yield Button("Remove Account", id="remove_account_button")
                    yield Button("Switch Account", id="switch_account_button")
                    yield Button("Back", id="back_button")
            
            with Vertical(id="add_account_container", classes="hidden"):
                yield Static("Add New Account", classes="section_title")
                yield Input(placeholder="Username", id="username_input")
                yield Input(placeholder="Client ID", id="client_id_input")
                yield Input(placeholder="Client Secret", id="client_secret_input")
                yield Input(placeholder="Password", id="password_input", password=True)
                
                with Horizontal(id="add_account_actions"):
                    yield Button("Add", id="confirm_add_button")
                    yield Button("Cancel", id="cancel_add_button")

    def on_mount(self):
        self.logger.info("AccountManagementScreen mounted")
        self.load_accounts()
        self.refresh_accounts_list()

    def load_accounts(self):
        self.accounts = self.reddit_service.get_accounts()
        self.logger.info(f"Loaded {len(self.accounts)} accounts")

    def refresh_accounts_list(self):
        accounts_list = self.query_one("#accounts_list")
        accounts_list.remove_children()
        
        if not self.accounts:
            accounts_list.mount(Static("No accounts found. Add your first account!", classes="message-body"))
            return
        
        current_account = self.reddit_service.get_current_account()
        
        for i, username in enumerate(self.accounts):
            account_data = self.reddit_service.accounts.get(username, {})
            added_date = datetime.fromtimestamp(account_data.get("added_date", 0)).strftime("%Y-%m-%d")
            last_used = datetime.fromtimestamp(account_data.get("last_used", 0)).strftime("%Y-%m-%d %H:%M")
            
            is_current = username == current_account
            status_text = " (Current)" if is_current else ""
            
            account_box = Container(
                Static(f"{username}{status_text}", classes="account-name"),
                Static(f"Added: {added_date}", classes="account-date"),
                Static(f"Last used: {last_used}", classes="account-date"),
                classes=f"account {'current' if is_current else ''} {'selected' if i == self.selected_index else ''}",
                id=f"account_{username}"
            )
            accounts_list.mount(account_box)

    def on_key(self, event):
        if self.mode == "list":
            if event.key == "up":
                self.selected_index = max(0, self.selected_index - 1)
                self._update_selection()
                event.prevent_default()
            elif event.key == "down":
                self.selected_index = min(len(self.accounts) - 1, self.selected_index + 1)
                self._update_selection()
                event.prevent_default()
            elif event.key == "enter":
                if 0 <= self.selected_index < len(self.accounts):
                    self.switch_to_account(self.accounts[self.selected_index])
                event.prevent_default()
        
        return event

    def _update_selection(self):
        for i, username in enumerate(self.accounts):
            account_box = self.query_one(f"#account_{username}")
            if i == self.selected_index:
                account_box.add_class("selected")
            else:
                account_box.remove_class("selected")

    def switch_to_account(self, username):
        self.logger.info(f"Switching to account: {username}")
        if self.reddit_service.switch_account(username):
            self.notify(f"Switched to account: {username}", severity="information")
            self.dismiss({"action": "switch", "account": username})
        else:
            self.notify(f"Failed to switch to account: {username}", severity="error")

    def on_button_pressed(self, event: Button.Pressed):
        button_id = event.button.id
        
        if button_id == "add_account_button":
            self.show_add_account_form()
        elif button_id == "remove_account_button":
            if 0 <= self.selected_index < len(self.accounts):
                self.remove_account(self.accounts[self.selected_index])
        elif button_id == "switch_account_button":
            if 0 <= self.selected_index < len(self.accounts):
                self.switch_to_account(self.accounts[self.selected_index])
        elif button_id == "back_button":
            self.dismiss({"action": "back"})
        elif button_id == "confirm_add_button":
            self.add_account()
        elif button_id == "cancel_add_button":
            self.show_account_list()

    def show_add_account_form(self):
        self.mode = "add"
        self.query_one("#account_list_container").add_class("hidden")
        self.query_one("#add_account_container").remove_class("hidden")
        self.query_one("#username_input").focus()

    def show_account_list(self):
        self.mode = "list"
        self.query_one("#account_list_container").remove_class("hidden")
        self.query_one("#add_account_container").add_class("hidden")
        self.refresh_accounts_list()

    def add_account(self):
        username = self.query_one("#username_input").value.strip()
        client_id = self.query_one("#client_id_input").value.strip()
        client_secret = self.query_one("#client_secret_input").value.strip()
        password = self.query_one("#password_input").value.strip()
        
        if not all([username, client_id, client_secret, password]):
            self.notify("Please fill in all fields", severity="warning")
            return
        
        if username in self.accounts:
            self.notify(f"Account {username} already exists", severity="warning")
            return
        
        if self.reddit_service.add_account(username, client_id, client_secret, password):
            self.notify(f"Account {username} added successfully", severity="information")
            self.load_accounts()
            self.show_account_list()
            self.clear_form()
        else:
            self.notify(f"Failed to add account {username}", severity="error")

    def remove_account(self, username):
        if username == self.reddit_service.get_current_account():
            self.notify("Cannot remove the currently active account", severity="warning")
            return
        
        if self.reddit_service.remove_account(username):
            self.notify(f"Account {username} removed successfully", severity="information")
            self.load_accounts()
            self.refresh_accounts_list()
        else:
            self.notify(f"Failed to remove account {username}", severity="error")

    def clear_form(self):
        self.query_one("#username_input").value = ""
        self.query_one("#client_id_input").value = ""
        self.query_one("#client_secret_input").value = ""
        self.query_one("#password_input").value = "" 