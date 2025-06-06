from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Input, Button, Static
from textual.screen import ModalScreen
from utils.logger import Logger
from services.reddit_service import RedditService

class LoginScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        Logger().info("Composing LoginScreen UI")
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
        Logger().info(f"Button pressed: {event.button.id}")
        if event.button.id == "login_button":
            client_id = self.query_one("#client_id").value
            client_secret = self.query_one("#client_secret").value
            username = self.query_one("#username").value
            password = self.query_one("#password").value

            Logger().info(f"Collected credentials: client_id={'***' if client_id else ''}, username={username}")

            if not all([client_id, client_secret, username, password]):
                Logger().warning("Login attempt with missing fields")
                self.notify("Please fill in all fields", severity="error")
                return

            Logger().info("All fields filled, attempting login")
            reddit_service = RedditService()
            if reddit_service.login(client_id, client_secret, username, password):
                Logger().info("Login successful")
                self.notify("Login successful!", severity="success")
                self.dismiss(True)
            else:
                Logger().warning("Login failed")
                self.notify("Login failed. Please check your credentials.", severity="error") 