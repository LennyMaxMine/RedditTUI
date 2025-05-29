from blessed import Terminal
from ui.widgets.sidebar import Sidebar
from ui.widgets.post_list import PostList
from ui.widgets.post_view import PostView
from ui.widgets.post_options_view import PostOptionsScreen
from ui.widgets.header import Header
from ui.screens.login_screen import LoginScreen
from ui.screens.search_screen import SearchScreen
from ui.screens.help_screen import HelpScreen
from ui.screens.settings_screen import SettingsScreen
from ui.screens.subreddits_screen import SubredditsScreen
from ui.screens.user_profile_screen import UserProfileScreen
from services.settings_service import Settings
import praw
import time
import json
import os

class RedditTUI:
    def __init__(self):
        self.term = Terminal()
        self.settings = Settings()
        self.settings.load_settings_from_file()
        self.sidebar = Sidebar(self.term)
        self.post_list = PostList(self.term)
        self.post_view = PostView(self.term)
        self.post_options_view = PostOptionsScreen(self.term)
        self.header = Header(self.term)
        self.reddit_instance = None
        self.login_screen = LoginScreen(self.reddit_instance)
        self.reddit_instance = self.login_screen.reddit_instance
        self.search_screen = SearchScreen(self.term, self.reddit_instance)
        self.help_screen = HelpScreen(self.term)
        self.settings_screen = SettingsScreen(self.term)
        self.settings_screen.reddit_instance = self.reddit_instance
        self.subreddits_screen = SubredditsScreen(self.term, self.reddit_instance)
        self.user_profile_screen = UserProfileScreen(self.term, self.reddit_instance)
        self.search_screen.reddit_instance = self.reddit_instance
        self.subreddits_screen.reddit_instance = self.reddit_instance
        self.user_profile_screen.reddit_instance = self.reddit_instance
        self.last_loaded_post = None
        self.current_feed = 'home'
        
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
                    self.over18 = False
                    self.stickied = False

            test_posts = [
                MockPost("Welcome to Reddit TUI", "reddit", 100, 50),
                MockPost("This is a test post", "test", 50, self.settings.posts_per_page),
                MockPost("Another test post", "test", 75, 30)
            ]
            self.post_list.update_posts(test_posts)

        self.current_screen = 'home'
        self.active_component = 'sidebar'
        self.post_options_view.reddit_instance = self.reddit_instance

    def handle_sidebar_option(self, option):
        if option in ['Home', 'New', 'Top']:
            self.current_screen = 'home'
            self.active_component = 'post_list'
            self.current_feed = option.lower()
            self.update_posts_from_reddit()
        elif option == "Saved":
            if self.reddit_instance:
                self.current_screen = 'home'
                #self.active_component = 'post_list'
                self.current_feed = 'saved'
                self.update_saved_posts()
            else:
                print(self.term.move(self.term.height - 3, 0) + self.term.red("Please login first"))
        elif option == "Search":
            self.current_screen = 'search'
            self.search_screen.reddit_instance = self.reddit_instance
            self.header.update_title("RedditTUI")
        elif option == "Login":
            self.show_login_screen()
        elif option == "Help":
            self.current_screen = 'help'
            self.header.update_title("RedditTUI")
        elif option == "Settings":
            self.current_screen = 'settings'
            self.header.update_title("RedditTUI")
        elif option == "Subreddits":
            self.current_screen = 'subreddits'
            self.subreddits_screen.reddit_instance = self.reddit_instance
            self.subreddits_screen.load_subreddits()
            self.header.update_title("RedditTUI")
        elif option == "Profile":
            if self.reddit_instance:
                self.current_screen = 'profile'
                self.user_profile_screen.load_user(self.reddit_instance.user.me().name)
                self.header.update_title(f"RedditTUI - Profile: {self.reddit_instance.user.me().name}")
            else:
                print(self.term.move(self.term.height - 3, 0) + self.term.red("Please login first"))
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
            self.settings_screen.reddit_instance = self.reddit_instance
            print(self.term.move(self.term.height - 2, 0) + self.term.green("Login successful!"))
            time.sleep(0.5)
            #input()
        else:
            self.header.update_title("Reddit TUI - Not logged in")
            print(self.term.move(self.term.height - 2, 0) + self.term.red("Login failed. Press Enter to continue..."))
            input()

    def update_posts_from_reddit(self, load_more=False):
        self.post_list.current_page = self.current_feed
        if self.reddit_instance:
            try:
                if load_more and self.last_loaded_post:
                    if self.current_feed == 'home':
                        posts = list(self.reddit_instance.front.hot(limit=self.settings.posts_per_page, after=self.last_loaded_post))
                    elif self.current_feed == 'new':
                        posts = list(self.reddit_instance.front.new(limit=self.settings.posts_per_page, after=self.last_loaded_post))
                    elif self.current_feed == 'top':
                        posts = list(self.reddit_instance.front.top(limit=self.settings.posts_per_page, after=self.last_loaded_post))
                else:
                    if self.current_feed == 'home':
                        posts = list(self.reddit_instance.front.hot(limit=self.settings.posts_per_page))
                    elif self.current_feed == 'new':
                        posts = list(self.reddit_instance.front.new(limit=self.settings.posts_per_page))
                    elif self.current_feed == 'top':
                        posts = list(self.reddit_instance.front.top(limit=self.settings.posts_per_page))
                
                if not self.settings.show_nsfw:
                    posts = [post for post in posts if not post.over_18]
                
                if posts:
                    if load_more:
                        self.post_list.append_posts(posts)
                    else:
                        self.post_list.update_posts(posts)
                    self.last_loaded_post = posts[-1].fullname
                    self.post_list.loading_more = False
                    self.header.update_title(f"RedditTUI - {self.current_feed.capitalize()} Feed")
                    print(self.term.move(self.term.height - 3, 0) + self.term.green(f"Successfully loaded {len(posts)} posts"))
                else:
                    print(self.term.move(self.term.height - 3, 0) + self.term.yellow("No more posts found"))
            except Exception as e:
                print(self.term.move(self.term.height - 3, 0) + self.term.red(f"Error fetching posts: {e}"))
                with open("temp.txt", "w") as f:
                    f.write(str(e))
                self.post_list.loading_more = False

    def load_post_comments(self, post):
        if not post or not hasattr(post, 'comments'):
            return []
        try:
            if self.settings.auto_load_comments:
                depth = max(0, min(self.settings.comment_depth, 10))
                post.comments.replace_more(limit=depth)
            else:
                post.comments.replace_more(limit=0)
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
        elif self.current_screen == 'post_options':
            post_options_lines = self.post_options_view.display().split('\n')
            available_lines = content_height
            for i, line in enumerate(post_options_lines):
                if i < available_lines:
                    print(self.term.move(i + 3, 22) + line)
        elif self.current_screen == 'search':
            search_lines = self.search_screen.display().split('\n')
            available_lines = content_height
            for i, line in enumerate(search_lines):
                if i < available_lines:
                    print(self.term.move(i + 3, 22) + line)
        elif self.current_screen == 'help':
            help_lines = self.help_screen.display().split('\n')
            available_lines = content_height
            for i, line in enumerate(help_lines):
                if i < available_lines:
                    print(self.term.move(i + 3, 22) + line)
        elif self.current_screen == 'settings':
            settings_lines = self.settings_screen.display().split('\n')
            available_lines = content_height
            for i, line in enumerate(settings_lines):
                if i < available_lines:
                    print(self.term.move(i + 3, 22) + line)
        elif self.current_screen == 'subreddits':
            subreddits_lines = self.subreddits_screen.display().split('\n')
            available_lines = content_height
            for i, line in enumerate(subreddits_lines):
                if i < available_lines:
                    print(self.term.move(i + 3, 22) + line)
        elif self.current_screen == 'profile':
            profile_lines = self.user_profile_screen.display().split('\n')
            available_lines = content_height
            for i, line in enumerate(profile_lines):
                if i < available_lines:
                    print(self.term.move(i + 3, 22) + line)

    def update_posts_from_subreddit(self, subreddit, category="hot"):
        if self.reddit_instance:
            try:
                if category == "hot":
                    posts = list(subreddit.hot(limit=self.settings.posts_per_page))
                elif category == "new":
                    posts = list(subreddit.new(limit=self.settings.posts_per_page))
                elif category == "top":
                    posts = list(subreddit.top(limit=self.settings.posts_per_page))
                elif category == "rising":
                    posts = list(subreddit.rising(limit=self.settings.posts_per_page))
                else:
                    posts = list(subreddit.hot(limit=self.settings.posts_per_page))

                if not self.settings.show_nsfw:
                    posts = [post for post in posts if not post.over_18]

                if posts:
                    self.post_list.update_posts(posts)
                    self.last_loaded_post = posts[-1].fullname
                    self.post_list.loading_more = False
            except Exception as e:
                print(self.term.move(self.term.height - 3, 0) + 
                      self.term.red(f"Error fetching {category} posts: {e}"))
                self.post_list.loading_more = False

    def update_saved_posts(self, load_more=False):
        if self.reddit_instance:
            try:
                if load_more and self.last_loaded_post:
                    saved_items = list(self.reddit_instance.user.me().saved(limit=self.settings.posts_per_page, after=self.last_loaded_post))
                else:
                    saved_items = list(self.reddit_instance.user.me().saved(limit=self.settings.posts_per_page))
                
                posts = []
                for item in saved_items:
                    if hasattr(item, 'title'):  # It's a post
                        posts.append(item)
                    else:  # It's a comment
                        posts.append(item.submission)
                
                if not self.settings.show_nsfw:
                    posts = [post for post in posts if not post.over_18]
                
                if posts:
                    if load_more:
                        self.post_list.append_posts(posts)
                    else:
                        self.post_list.update_posts(posts)
                    self.last_loaded_post = posts[-1].fullname
                    self.post_list.loading_more = False
                    self.header.update_title("RedditTUI - Saved Items")
                    print(self.term.move(self.term.height - 3, 0) + self.term.green(f"Successfully loaded {len(posts)} saved items"))
                else:
                    print(self.term.move(self.term.height - 3, 0) + self.term.yellow("No more saved items found"))
            except Exception as e:
                print(self.term.move(self.term.height - 3, 0) + self.term.red(f"Error fetching saved items: {e}"))
                self.post_list.loading_more = False

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
                        if self.current_screen == 'post_options':
                            if self.post_options_view.confirming_report:
                                self.post_options_view.confirming_report = False
                                self.post_options_view.selected_reason = None
                            else:
                                self.current_screen = 'post'
                        elif self.current_screen == 'post':
                            if self.post_view.from_search:
                                self.current_screen = 'search'
                                self.post_view.from_search = False
                            else:
                                self.current_screen = 'home'
                                self.active_component = 'post_list'
                                self.post_view.current_post = None
                                self.post_view.comments = []
                        elif self.current_screen in ['search', 'help', 'settings', 'subreddits', 'profile']:
                            if self.current_screen == 'search':
                                self.search_screen.clear_query()
                            self.current_screen = 'home'
                            self.active_component = 'sidebar'
                            self.header.update_title(f"RedditTUI - {self.current_feed.capitalize()} Feed")
                            self.update_posts_from_reddit()
                        elif self.current_screen == 'home' and self.active_component == 'post_list':
                            self.active_component = 'sidebar'
                        continue
                    elif key == '\x1b[A':  # Up Arrow
                        if self.active_component == 'sidebar':
                            self.sidebar.navigate("up")
                            selected_option = self.sidebar.get_selected_option()
                            if selected_option in ['Home', 'New', 'Top']:
                                self.current_feed = selected_option.lower()
                                self.current_screen = 'home'
                                #self.active_component = 'post_list'
                                self.update_posts_from_reddit()
                            else:
                                self.handle_sidebar_option(selected_option)
                        elif self.current_screen == 'home':
                            self.post_list.scroll_up()
                        elif self.current_screen == 'post':
                            self.post_view.scroll_comments_up()
                        elif self.current_screen == 'search':
                            self.search_screen.scroll_up()
                        elif self.current_screen == 'subreddits':
                            self.subreddits_screen.scroll_up()
                        elif self.current_screen == 'settings':
                            if self.settings_screen.theme_screen_activated != True:
                                self.settings_screen.previous_option()
                            else:
                                self.settings_screen.theme_scroll_up()
                        elif self.current_screen == 'profile':
                            self.user_profile_screen.scroll_up()
                        elif self.settings_screen.theme_screen_activated == True:
                            self.settings_screen.theme_scroll_up()
                    elif key == '\x1b[B':  # Down Arrow
                        if self.active_component == 'sidebar':
                            self.sidebar.navigate("down")
                            selected_option = self.sidebar.get_selected_option()
                            if selected_option in ['Home', 'New', 'Top']:
                                self.current_feed = selected_option.lower()
                                self.current_screen = 'home'
                                #self.active_component = 'post_list'
                                self.update_posts_from_reddit()
                            else:
                                self.handle_sidebar_option(selected_option)
                        elif self.current_screen == 'home':
                            self.post_list.scroll_down()
                        elif self.current_screen == 'post':
                            self.post_view.scroll_comments_down()
                        elif self.current_screen == 'search':
                            self.search_screen.scroll_down()
                        elif self.current_screen == 'subreddits':
                            self.subreddits_screen.scroll_down()
                        elif self.current_screen == 'settings':
                            if self.settings_screen.theme_screen_activated != True:
                                self.settings_screen.next_option()
                            else:
                                self.settings_screen.theme_scroll_down()
                        elif self.current_screen == 'profile':
                            self.user_profile_screen.scroll_down()
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
                        elif self.current_screen == 'settings':
                            if self.settings_screen.next_value():
                                self.current_screen = 'settings'
                                self.active_component = 'sidebar'
                        elif self.current_screen == 'subreddits':
                            self.subreddits_screen.next_category()
                    elif key == '\x1b[D':  # Left Arrow
                        if self.current_screen == 'post':
                            self.current_screen = 'home'
                            self.active_component = 'post_list'
                            self.post_view.current_post = None
                            self.post_view.comments = []
                        elif self.current_screen == 'home' and self.active_component == 'post_list':
                            self.active_component = 'sidebar'
                        elif self.current_screen == 'settings':
                            self.settings_screen.next_value()
                        elif self.current_screen == 'subreddits':
                            self.subreddits_screen.previous_category()
                    elif key == 'k':  # Upvote
                        if self.current_screen == 'post':
                            self.post_view.upvote_post()
                    elif key == 'j':  # Downvote
                        if self.current_screen == 'post':
                            self.post_view.downvote_post()
                    elif key == '\t':  # Tab
                        if self.current_screen == 'search':
                            self.search_screen.next_search_type()
                        elif self.current_screen == 'help':
                            self.help_screen.next_section()
                        elif self.current_screen == 'settings':
                            if self.settings_screen.next_value():
                                self.current_screen = 'home'
                                self.active_component = 'sidebar'
                        elif self.current_screen == 'subreddits':
                            self.subreddits_screen.next_category()
                    elif key == '\x7f':  # Backspace
                        if self.current_screen == 'search':
                            self.search_screen.backspace()
                    elif len(key) == 1 and key.isprintable():  # Regular character input
                        if self.current_screen == 'search':
                            self.search_screen.add_char(key)
                            self.active_component = 'post_list'
                        elif key.lower() == "o" and self.current_screen == 'post':
                            self.post_options_view.current_post = self.post_view.current_post
                            self.current_screen = 'post_options'
                        elif self.current_screen == 'post_options':
                            result = self.post_options_view.handle_input(key)
                            if result == "reported":
                                print(self.term.move(self.term.height - 3, 0) + self.term.green("Post reported successfully"))
                                time.sleep(1)
                                self.current_screen = 'post'
                            elif result == "view_post":
                                comments = self.load_post_comments(self.post_options_view.current_post)
                                self.post_view.display_post(self.post_options_view.current_post, comments)
                                self.current_screen = 'post'
                            elif result and result.startswith("error:"):
                                print(self.term.move(self.term.height - 3, 0) + self.term.red(f"Error reporting post: {result[6:]}"))
                                time.sleep(1)
                            self.render()
                    elif key in ['\r', '\n', '\x0a', '\x0d', '\x1b\x0d', '\x1b\x0a']:  # Enter
                        if self.current_screen == 'post_options':
                            result = self.post_options_view.handle_input(key)
                            if result == "reported":
                                print(self.term.move(self.term.height - 3, 0) + self.term.green("Post reported successfully"))
                                time.sleep(1)
                                self.current_screen = 'post'
                            elif result == "view_post":
                                comments = self.load_post_comments(self.post_options_view.current_post)
                                self.post_view.display_post(self.post_options_view.current_post, comments)
                                self.current_screen = 'post'
                            elif result and result.startswith("error:"):
                                print(self.term.move(self.term.height - 3, 0) + self.term.red(f"Error reporting post: {result[6:]}"))
                                time.sleep(1)
                            self.render()
                        elif self.active_component == 'sidebar':
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
                        elif self.current_screen == 'settings':
                            if self.settings_screen.handle_enter():
                                self.current_screen = 'settings'
                                self.active_component = 'sidebar'
                        elif self.current_screen == 'subreddits':
                            selected_subreddit, category = self.subreddits_screen.get_selected_subreddit()
                            if selected_subreddit:
                                self.current_screen = 'home'
                                self.active_component = 'post_list'
                                self.update_posts_from_subreddit(selected_subreddit, category)
        finally:
            print(self.term.exit_fullscreen())

if __name__ == '__main__':
    app = RedditTUI()
    app.run()