from blessed import Terminal
from ui.widgets.sidebar import Sidebar
from ui.widgets.post_list import PostList
from ui.widgets.post_view import PostView
from ui.widgets.header import Header

class RedditTUI:
    def __init__(self):
        self.term = Terminal()
        self.sidebar = Sidebar(self.term)
        self.post_list = PostList(self.term)
        self.post_view = PostView(self.term)
        self.header = Header(self.term)

        class MockPost:
            def __init__(self, title, subreddit, score, num_comments):
                self.title = title
                self.subreddit = type('Subreddit', (), {'display_name': subreddit})
                self.score = score
                self.num_comments = num_comments

        test_posts = [
            MockPost("Welcome to Reddit TUI", "reddit", 100, 50),
            MockPost("This is a test post", "test", 50, 25),
            MockPost("Another test post", "test", 75, 30)
        ]
        self.post_list.update_posts(test_posts)

        self.current_screen = 'home'
        self.active_component = 'sidebar'

    def handle_sidebar_option(self, option):
        print(self.term.move(self.term.height - 4, 0) + f"Handling option: {option}")
        if option == "View Post":
            self.active_component = 'post_list'
        elif option == "Login":
            # TODO: Implement login functionality
            print(self.term.move(self.term.height - 3, 0) + "Login functionality coming soon!")
        elif option == "Help":
            # TODO: Implement help screen
            print(self.term.move(self.term.height - 3, 0) + "Help screen coming soon!")
        elif option == "Exit":
            return True
        return False
    
    def render(self):
        # Clear screen and move cursor to top-left
        print(self.term.clear())
        print(self.term.move(0, 0))
        
        print(self.header.display())
        
        # Print sidebar
        sidebar_lines = self.sidebar.display().split('\n')
        for i, line in enumerate(sidebar_lines):
            print(self.term.move(i + 3, 0) + line)
        
        post_list_lines = self.post_list.display().split('\n')
        for i, line in enumerate(post_list_lines):
            print(self.term.move(i + 3, 22) + line)

        post_view_lines = self.post_view.display().split('\n')
        for i, line in enumerate(post_view_lines):
            print(self.term.move(i + 3, 60) + line)

    def run(self):
        print(self.term.enter_fullscreen())
        
        try:
            # Enable cbreak mode for better keyboard handling
            with self.term.cbreak(), self.term.hidden_cursor():
                while True:
                    self.render()
                    key = self.term.inkey()
                    
                    if key.lower() == 'q':
                        break
                    elif key == '\x1b[A':  # Up arrow
                        if self.active_component == 'sidebar':
                            self.sidebar.navigate("up")
                        else:
                            self.post_list.scroll_up()
                    elif key == '\x1b[B':  # Down arrow
                        if self.active_component == 'sidebar':
                            self.sidebar.navigate("down")
                        else:
                            self.post_list.scroll_down()
                    elif key in ['\r', '\n', '\x0a', '\x0d', '\x1b\x0d', '\x1b\x0a']:
                        print(self.term.move(self.term.height - 2, 0) + f"Enter pressed! Active: {self.active_component}")
                        if self.active_component == 'sidebar':
                            selected_option = self.sidebar.get_selected_option()
                            print(self.term.move(self.term.height - 3, 0) + f"Selected option: {selected_option}")
                            print(self.term.move(self.term.height - 5, 0) + f"Key code: {[hex(ord(c)) for c in key]}")
                            if self.handle_sidebar_option(selected_option):
                                break
                        else:
                            pass
        finally:
            print(self.term.exit_fullscreen())

if __name__ == '__main__':
    app = RedditTUI()
    app.run()