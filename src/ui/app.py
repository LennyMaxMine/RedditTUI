from blessed import Terminal
from ui.widgets.sidebar import Sidebar
from ui.widgets.post_list import PostList
from ui.widgets.post_view import PostView
from ui.widgets.header import Header
from ui.screens.login_screen import LoginScreen
from ui.screens.search_screen import SearchScreen
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
        self.search_screen = SearchScreen(self.term, self.reddit_instance)
        self.reddit_instance = self.login_screen.reddit_instance
        self.search_screen.reddit_instance = self.reddit_instance
        self.last_loaded_post = None

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
                    self.author = "test_user"
                    self.over_18 = False
                    self.stickied = False

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
        if option == "Search":
            self.current_screen = 'search'
            self.search_screen.reddit_instance = self.reddit_instance
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

    def update_posts_from_reddit(self, load_more=False):
        if self.reddit_instance:
            try:
                if load_more and self.last_loaded_post:
                    # Load more posts after the last loaded post
                    posts = list(self.reddit_instance.front.hot(limit=25, after=self.last_loaded_post))
                else:
                    # Initial load
                    posts = list(self.reddit_instance.front.hot(limit=25))
                
                if posts:
                    if load_more:
                        self.post_list.append_posts(posts)
                    else:
                        self.post_list.update_posts(posts)
                    self.last_loaded_post = posts[-1].fullname
                    self.post_list.loading_more = False
                    print(self.term.move(self.term.height - 3, 0) + self.term.green(f"Successfully loaded {len(posts)} posts"))
                else:
                    print(self.term.move(self.term.height - 3, 0) + self.term.yellow("No more posts found"))
            except Exception as e:
                print(self.term.move(self.term.height - 3, 0) + self.term.red(f"Error fetching posts: {e}"))
                self.post_list.loading_more = False

    def load_post_comments(self, post):
        """Load comments for a post efficiently"""
        if not post or not hasattr(post, 'comments'):
            return []
        try:
            post.comments.replace_more(limit=0)  # Don't load MoreComments objects initially
            return list(post.comments.list())
        except Exception as e:
            print(self.term.move(self.term.height - 3, 0) + self.term.red(f"Error loading comments: {e}"))
            return []

    def render(self):
        print(self.term.clear())
        print(self.term.move(0, 0))
        
        print(self.header.display())
        
        content_height = self.term.height - 3
        
        sidebar_lines = self.sidebar.display().split('\n')
        for i, line in enumerate(sidebar_lines):
            if i < content_height:
                print(self.term.move(i + 3, 0) + line)
        
        if self.current_screen == 'home':
            post_list_lines = self.post_list.display().split('\n')
            available_lines = content_height
            for i, line in enumerate(post_list_lines):
                if i < available_lines:
                    print(self.term.move(i + 3, 22) + line)
        elif self.current_screen == 'post':
            post_view_lines = self.post_view.display().split('\n')
            available_lines = content_height
            for i, line in enumerate(post_view_lines):
                if i < available_lines:
                    print(self.term.move(i + 3, 22) + line)
        elif self.current_screen == 'search':
            search_lines = self.search_screen.display().split('\n')
            available_lines = content_height
            for i, line in enumerate(search_lines):
                if i < available_lines:
                    print(self.term.move(i + 3, 22) + line)

    def run(self):
        print(self.term.enter_fullscreen())
        
        try:
            with self.term.cbreak(), self.term.hidden_cursor():
                while True:
                    self.render()
                    key = self.term.inkey()
                    
                    if key.lower() == 'q':  # Quit
                        break
                    elif key == '\x1b':  # Escape
                        if self.current_screen == 'post':
                            if self.post_view.from_search:
                                self.current_screen = 'search'
                                self.post_view.from_search = False
                            else:
                                self.current_screen = 'home'
                                self.active_component = 'post_list'
                            self.post_view.current_post = None
                            self.post_view.comments = []
                        elif self.current_screen == 'search':
                            self.current_screen = 'home'
                            self.active_component = 'sidebar'
                        elif self.current_screen == 'home' and self.active_component == 'post_list':
                            self.active_component = 'sidebar'
                        continue
                    elif key == '\x1b[A':  # Up Arrow
                        if self.active_component == 'sidebar':
                            self.sidebar.navigate("up")
                        elif self.current_screen == 'home':
                            self.post_list.scroll_up()
                        elif self.current_screen == 'post':
                            self.post_view.scroll_comments_up()
                        elif self.current_screen == 'search':
                            self.search_screen.scroll_up()
                    elif key == '\x1b[B':  # Down Arrow
                        if self.active_component == 'sidebar':
                            self.sidebar.navigate("down")
                        elif self.current_screen == 'home':
                            if self.post_list.scroll_down():
                                self.update_posts_from_reddit(load_more=True)
                        elif self.current_screen == 'post':
                            if self.post_view.scroll_comments_down():
                                if self.post_view.need_more_comments:
                                    self.load_more_comments(self.post_view.current_post)
                        elif self.current_screen == 'search':
                            self.search_screen.scroll_down()
                    elif key == '\x1b[C':  # Right Arrow
                        if self.current_screen == 'home' and self.active_component == 'sidebar':
                            self.active_component = 'post_list'
                        elif self.current_screen == 'home' and self.active_component == 'post_list':
                            selected_post = self.post_list.get_selected_post()
                            if selected_post:
                                comments = self.load_post_comments(selected_post)
                                self.post_view.display_post(selected_post, comments)
                                self.post_view.from_search = False
                                self.current_screen = 'post'
                        elif self.current_screen == 'search':
                            selected_post = self.search_screen.get_selected_post()
                            if selected_post:
                                comments = self.load_post_comments(selected_post)
                                self.post_view.display_post(selected_post, comments)
                                self.post_view.from_search = True
                                self.current_screen = 'post'
                    elif key == '\x1b[D':  # Left Arrow
                        if self.current_screen == 'post':
                            self.current_screen = 'home'
                            self.active_component = 'post_list'
                            self.post_view.current_post = None
                            self.post_view.comments = []
                        elif self.current_screen == 'home' and self.active_component == 'post_list':
                            self.active_component = 'sidebar'
                    elif key == '\t':  # Tab
                        if self.current_screen == 'search':
                            self.search_screen.next_search_type()
                    elif key == '\x7f':  # Backspace
                        if self.current_screen == 'search':
                            self.search_screen.backspace()
                    elif key in ['\r', '\n', '\x0a', '\x0d', '\x1b\x0d', '\x1b\x0a']:  # Enter
                        if self.active_component == 'sidebar':
                            selected_option = self.sidebar.get_selected_option()
                            if self.handle_sidebar_option(selected_option):
                                break
                            else:
                                self.active_component = 'post_list'
                        elif self.current_screen == 'home' and self.active_component == 'post_list':
                            selected_post = self.post_list.get_selected_post()
                            if selected_post:
                                comments = self.load_post_comments(selected_post)
                                self.post_view.display_post(selected_post, comments)
                                self.post_view.from_search = False
                                self.current_screen = 'post'
                        elif self.current_screen == 'search':
                            selected_post = self.search_screen.get_selected_post()
                            if selected_post:
                                comments = self.load_post_comments(selected_post)
                                self.post_view.display_post(selected_post, comments)
                                self.post_view.from_search = True
                                self.current_screen = 'post'
                    elif len(key) == 1 and key.isprintable():  # Regular characters
                        if self.current_screen == 'search':
                            self.search_screen.add_char(key)
                            self.search_screen.search()
        finally:
            print(self.term.exit_fullscreen())

if __name__ == '__main__':
    app = RedditTUI()
    app.run()