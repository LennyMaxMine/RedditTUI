from blessed import Terminal
from ui.widgets.sidebar import Sidebar
from ui.widgets.post_list import PostList
from ui.widgets.post_view import PostView
from ui.widgets.header import Header
from ui.screens.login_screen import LoginScreen
import praw

class RedditTUI:
    def __init__(self):
        self.term = Terminal()
        self.sidebar = Sidebar(self.term)
        self.post_list = PostList(self.term)
        self.post_view = PostView(self.term)
        self.header = Header(self.term)
        self.reddit_instance = None
        self.login_screen = LoginScreen(self.reddit_instance)
        self.reddit_instance = self.login_screen.reddit_instance

        if self.reddit_instance:
            self.header.update_title(f"Reddit TUI - Logged in as {self.reddit_instance.user.me().name}")
            self.update_posts_from_reddit()
        else:
            self.header.update_title("Reddit TUI - Not logged in")
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
            self.show_login_screen()
        elif option == "Help":
            print(self.term.move(self.term.height - 3, 0) + "Help screen coming soon!")
        elif option == "Exit":
            return True
        return False

    def show_login_screen(self):
        print(self.term.clear())
        self.login_screen.display()
        if self.login_screen.reddit_instance:
            self.reddit_instance = self.login_screen.reddit_instance
            self.header.update_title(f"Reddit TUI - Logged in as {self.reddit_instance.user.me().name}")
            self.update_posts_from_reddit()
            print(self.term.move(self.term.height - 2, 0) + self.term.green("Login successful! Press Enter to continue..."))
            input()
        else:
            self.header.update_title("Reddit TUI - Not logged in")
            print(self.term.move(self.term.height - 2, 0) + self.term.red("Login failed. Press Enter to continue..."))
            input()

    def update_posts_from_reddit(self):
        if self.reddit_instance:
            try:
                posts = list(self.reddit_instance.front.hot(limit=25))
                if posts:
                    self.post_list.update_posts(posts)
                    print(self.term.move(self.term.height - 3, 0) + self.term.green(f"Successfully loaded {len(posts)} posts"))
                else:
                    print(self.term.move(self.term.height - 3, 0) + self.term.yellow("No posts found"))
            except Exception as e:
                print(self.term.move(self.term.height - 3, 0) + self.term.red(f"Error fetching posts: {e}"))
    
    def render(self):
        print(self.term.clear())
        print(self.term.move(0, 0))
        
        print(self.header.display())
        
        sidebar_lines = self.sidebar.display().split('\n')
        for i, line in enumerate(sidebar_lines):
            print(self.term.move(i + 3, 0) + line)
        
        if self.current_screen == 'home':
            post_list_lines = self.post_list.display().split('\n')
            for i, line in enumerate(post_list_lines):
                print(self.term.move(i + 3, 22) + line)
        elif self.current_screen == 'post':
            post_view_lines = self.post_view.display().split('\n')
            for i, line in enumerate(post_view_lines):
                print(self.term.move(i + 3, 22) + line)

    def run(self):
        print(self.term.enter_fullscreen())
        
        try:
            with self.term.cbreak(), self.term.hidden_cursor():
                while True:
                    self.render()
                    key = self.term.inkey()
                    
                    if key.lower() == 'q':
                        break
                    elif key == '\x1b':  # Escape key
                        if self.current_screen == 'post':
                            self.current_screen = 'home'
                            self.active_component = 'post_list'
                            continue
                    elif key == '\x1b[A':  # Up arrow
                        if self.active_component == 'sidebar':
                            self.sidebar.navigate("up")
                        elif self.current_screen == 'home':
                            self.post_list.scroll_up()
                    elif key == '\x1b[B':  # Down arrow
                        if self.active_component == 'sidebar':
                            self.sidebar.navigate("down")
                        elif self.current_screen == 'home':
                            self.post_list.scroll_down()
                    elif key == '\x1b[5~':  # Page Up
                        if self.current_screen == 'home':
                            for _ in range(5):
                                self.post_list.scroll_up()
                    elif key == '\x1b[6~':  # Page Down
                        if self.current_screen == 'home':
                            for _ in range(5):
                                self.post_list.scroll_down()
                    elif key in ['\r', '\n', '\x0a', '\x0d', '\x1b\x0d', '\x1b\x0a']:
                        if self.active_component == 'sidebar':
                            selected_option = self.sidebar.get_selected_option()
                            if self.handle_sidebar_option(selected_option):
                                break
                        elif self.current_screen == 'home':
                            selected_post = self.post_list.get_selected_post()
                            if selected_post:
                                # Fetch top 5 comments if possible
                                comments = []
                                try:
                                    if hasattr(selected_post, 'comments'):
                                        selected_post.comments.replace_more(limit=0)
                                        comments = [c for c in selected_post.comments.list()[:5] if hasattr(c, 'body')]
                                except Exception as e:
                                    comments = []
                                self.post_view.display_post(selected_post, comments)
                                self.current_screen = 'post'
        finally:
            print(self.term.exit_fullscreen())

if __name__ == '__main__':
    app = RedditTUI()
    app.run()