from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer
from textual.binding import Binding

class RedditTUI(App):
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("h", "home", "Home", show=True),
        Binding("n", "new", "New", show=True),
        Binding("t", "top", "Top", show=True),
        Binding("s", "search", "Search", show=True),
        Binding("l", "login", "Login", show=True),
        Binding("?", "help", "Help", show=True),
        Binding("c", "settings", "Settings", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container()
        yield Footer()

    def action_quit(self) -> None:
        self.exit()

    def action_home(self) -> None:
        pass

    def action_new(self) -> None:
        pass

    def action_top(self) -> None:
        pass

    def action_search(self) -> None:
        pass

    def action_login(self) -> None:
        pass

    def action_help(self) -> None:
        pass

    def action_settings(self) -> None:
        pass

if __name__ == "__main__":
    app = RedditTUI()
    app.run()
