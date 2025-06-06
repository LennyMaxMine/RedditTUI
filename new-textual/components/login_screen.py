from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Input, Button, Static
from textual.screen import Screen

class LoginScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Container(
            Vertical(
                Static("Reddit Login", classes="title"),
                Input(placeholder="Client ID", id="client_id"),
                Input(placeholder="Client Secret", id="client_secret", password=True),
                Input(placeholder="Username", id="username"),
                Input(placeholder="Password", id="password", password=True),
                Button("Login", id="login_button"),
                id="login_form"
            ),
            id="login_container"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login_button":
            client_id = self.query_one("#client_id").value
            client_secret = self.query_one("#client_secret").value
            username = self.query_one("#username").value
            password = self.query_one("#password").value

            if not all([client_id, client_secret, username, password]):
                self.notify("Please fill in all fields", severity="error")
                return

            self.dismiss((client_id, client_secret, username, password)) 