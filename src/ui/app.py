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
from ui.screens.messages_screen import MessagesScreen
from services.settings_service import Settings
from utils.logger import Logger
import praw
import time
import json
import os

class RedditTUI:
    def __init__(self):
        self.term = Terminal()
        self.settings = Settings()
        self.settings.load_settings_from_file()
        self.logger = Logger()
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
        self.messages_screen = MessagesScreen(self.term, self.reddit_instance)
        self.search_screen.reddit_instance = self.reddit_instance
        self.subreddits_screen.reddit_instance = self.reddit_instance
        self.user_profile_screen.reddit_instance = self.reddit_instance
        self.messages_screen.reddit_instance = self.reddit_instance
        self.post_view.reddit_instance = self.reddit_instance
        self.last_loaded_post = None
        self.current_feed = 'home'
        self.is_loading = False
        self.loading_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.loading_index = 0
        self.last_loading_update = 0
        
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
        self.logger.info("RedditTUI initialized")

    def handle_sidebar_option(self, option):
        self.logger.info(f"Handling sidebar option: {option}")
        if option in ['Home', 'New', 'Top']:
            self.current_screen = 'home'
            self.active_component = 'post_list'
            self.current_feed = option.lower()
            self.update_posts_from_reddit()
        elif option == "Saved":
            if self.reddit_instance:
                self.current_screen = 'home'
                self.current_feed = 'saved'
                self.update_saved_posts()
            else:
                self.logger.warning("Attempted to access saved posts without being logged in")
                print(self.term.move(self.term.height - 3, 0) + self.term.red("Please login first"))
        elif option == "Messages":
            if self.reddit_instance:
                self.current_screen = 'messages'
                self.active_component = 'messages'
                self.messages_screen.load_messages()
                self.header.update_title("RedditTUI - Messages")
            else:
                self.logger.warning("Attempted to access messages without being logged in")
                print(self.term.move(self.term.height - 3, 0) + self.term.red("Please login first"))
        elif option == "Search":
            self.current_screen = 'search'
            self.search_screen.reddit_instance = self.reddit_instance
            self.header.update_title("RedditTUI")
            self.logger.info("Entered search screen")
        elif option == "Login":
            self.show_login_screen()
        elif option == "Help":
            self.current_screen = 'help'
            self.header.update_title("RedditTUI")
            self.logger.info("Entered help screen")
        elif option == "Settings":
            self.current_screen = 'settings'
            self.header.update_title("RedditTUI")
            self.logger.info("Entered settings screen")
        elif option == "Subreddits":
            self.current_screen = 'subreddits'
            self.subreddits_screen.reddit_instance = self.reddit_instance
            self.subreddits_screen.load_subreddits()
            self.header.update_title("RedditTUI")
            self.logger.info("Entered subreddits screen")
        elif option == "Profile":
            if self.reddit_instance:
                self.current_screen = 'profile'
                self.user_profile_screen.load_user(self.reddit_instance.user.me().name)
                self.header.update_title(f"RedditTUI - Profile: {self.reddit_instance.user.me().name}")
                self.logger.info(f"Entered profile screen for user: {self.reddit_instance.user.me().name}")
            else:
                self.logger.warning("Attempted to access profile without being logged in")
                print(self.term.move(self.term.height - 3, 0) + self.term.red("Please login first"))
        elif option == "Exit":
            self.logger.info("User selected exit option")
            return True
        return False

    def show_login_screen(self):
        self.logger.info("Showing login screen")
        print(self.term.clear())
        self.login_screen.display()
        if self.login_screen.reddit_instance:
            self.reddit_instance = self.login_screen.reddit_instance
            self.header.update_title(f"Reddit TUI - Logged in as {self.reddit_instance.user.me().name}")
            self.update_posts_from_reddit()
            self.settings_screen.reddit_instance = self.reddit_instance
            self.logger.info(f"Login successful for user: {self.reddit_instance.user.me().name}")
            print(self.term.move(self.term.height - 2, 0) + self.term.green("Login successful!"))
            time.sleep(0.5)
        else:
            self.logger.warning("Login failed")
            self.header.update_title("Reddit TUI - Not logged in")
            print(self.term.move(self.term.height - 2, 0) + self.term.red("Login failed. Press Enter to continue..."))
            input()

    def update_posts_from_reddit(self, load_more=False):
        self.post_list.current_page = self.current_feed
        if self.reddit_instance:
            self.is_loading = True
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
                    self.logger.info(f"Loaded {len(posts)} posts from {self.current_feed} feed")
                else:
                    print(self.term.move(self.term.height - 3, 0) + self.term.yellow("No more posts found"))
                    self.logger.warning("No more posts found")
            except Exception as e:
                error_msg = f"Error fetching posts: {e}"
                print(self.term.move(self.term.height - 3, 0) + self.term.red(error_msg))
                self.logger.error(error_msg, exc_info=True)
                self.post_list.loading_more = False
            finally:
                self.is_loading = False

    def load_post_comments(self, post):
        if not post or not hasattr(post, 'comments'):
            return []
        self.is_loading = True
        try:
            if self.settings.auto_load_comments:
                depth = max(0, min(self.settings.comment_depth, 10))
                post.comments.replace_more(limit=depth)
            else:
                post.comments.replace_more(limit=0)
            comments = list(post.comments.list())
            self.logger.info(f"Loaded {len(comments)} comments for post: {post.title}")
            return comments
        except Exception as e:
            error_msg = f"Error loading comments: {e}"
            print(self.term.move(self.term.height - 3, 0) + self.term.red(error_msg))
            self.logger.error(error_msg, exc_info=True)
            return []
        finally:
            self.is_loading = False

    def render(self):
        print(self.term.clear())
        print(self.term.move(0, 0))
        
        print(self.header.display())
        
        content_height = self.term.height - 3
        
        # Set sidebar active state
        self.sidebar.active = self.active_component == 'sidebar'
        
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
        elif self.current_screen == 'messages':
            messages_lines = self.messages_screen.display().split('\n')
            available_lines = content_height
            for i, line in enumerate(messages_lines):
                if i < available_lines:
                    print(self.term.move(i + 3, 22) + line)

        if self.is_loading:
            current_time = time.time()
            if current_time - self.last_loading_update >= 0.1:  # Update every 100ms
                self.loading_index = (self.loading_index + 1) % len(self.loading_chars)
                self.last_loading_update = current_time
            loading_text = f"{self.term.bright_blue(self.loading_chars[self.loading_index])} Loading..."
            print(self.term.move(self.term.height - 1, 0) + loading_text)

    def update_posts_from_subreddit(self, subreddit, category="hot"):
        if self.reddit_instance:
            self.is_loading = True
            try:
                self.logger.info(f"Loading {category} posts from subreddit: {subreddit.display_name}")
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
                    self.logger.info(f"Successfully loaded {len(posts)} posts from r/{subreddit.display_name}")
                else:
                    self.logger.warning(f"No posts found in r/{subreddit.display_name}")
            except Exception as e:
                error_msg = f"Error fetching {category} posts: {e}"
                self.logger.error(error_msg, exc_info=True)
                print(self.term.move(self.term.height - 3, 0) + self.term.red(error_msg))
                self.post_list.loading_more = False
            finally:
                self.is_loading = False

    def update_saved_posts(self, load_more=False):
        if self.reddit_instance:
            self.is_loading = True
            try:
                if load_more and self.last_loaded_post:
                    self.logger.info("Loading more saved posts")
                    saved_items = list(self.reddit_instance.user.me().saved(limit=self.settings.posts_per_page, after=self.last_loaded_post))
                else:
                    self.logger.info("Loading initial saved posts")
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
                    self.logger.info(f"Successfully loaded {len(posts)} saved items")
                    print(self.term.move(self.term.height - 3, 0) + self.term.green(f"Successfully loaded {len(posts)} saved items"))
                else:
                    self.logger.warning("No more saved items found")
                    print(self.term.move(self.term.height - 3, 0) + self.term.yellow("No more saved items found"))
            except Exception as e:
                error_msg = f"Error fetching saved items: {e}"
                self.logger.error(error_msg, exc_info=True)
                print(self.term.move(self.term.height - 3, 0) + self.term.red(error_msg))
                self.post_list.loading_more = False
            finally:
                self.is_loading = False

    def run(self):
        print(self.term.enter_fullscreen())
        self.logger.info("Starting RedditTUI")
        
        try:
            with self.term.cbreak(), self.term.hidden_cursor():
                while True:
                    try:
                        self.sidebar.active = self.active_component == 'sidebar'
                        self.post_list.active = self.active_component == 'post_list'
                        self.messages_screen.active = self.active_component == 'messages'
                        print(self.term.move(self.term.height - 2, 0) + f"Active component: {self.active_component}, Messages active: {self.messages_screen.active}")
                        self.render()
                        key = self.term.inkey()
                        
                        if key.lower() == 'q':  # Quit
                            self.logger.info("User quit application")
                            break
                        elif key == '\x1b':  # Escape
                            self.logger.debug("Escape key pressed")
                            if self.current_screen == 'post_options':
                                if self.post_options_view.confirming_report:
                                    self.post_options_view.confirming_report = False
                                    self.post_options_view.selected_reason = None
                                else:
                                    self.current_screen = 'post'
                            elif self.current_screen == 'post':
                                if self.post_view.comment_mode:
                                    self.post_view.comment_mode = False
                                    self.post_view.comment_text = ""
                                    self.post_view.comment_cursor_pos = 0
                                elif self.post_view.from_search:
                                    self.current_screen = 'search'
                                    self.post_view.from_search = False
                                else:
                                    self.current_screen = 'home'
                                    self.active_component = 'post_list'
                                    self.post_view.current_post = None
                                    self.post_view.comments = []
                            elif self.current_screen in ['search', 'help', 'settings', 'subreddits', 'profile', 'messages']:
                                if self.current_screen == 'search':
                                    self.search_screen.clear_query()
                                elif self.current_screen == 'messages' and self.messages_screen.compose_mode:
                                    self.messages_screen.compose_mode = False
                                    self.messages_screen.recipient = ""
                                    self.messages_screen.subject = ""
                                    self.messages_screen.message_text = ""
                                    self.messages_screen.cursor_pos = 0
                                    self.messages_screen.current_field = "recipient"
                                    continue
                                self.current_screen = 'home'
                                self.active_component = 'sidebar'
                                self.header.update_title(f"RedditTUI - {self.current_feed.capitalize()} Feed")
                                self.update_posts_from_reddit()
                            elif self.current_screen == 'home' and self.active_component == 'post_list':
                                self.active_component = 'sidebar'
                            continue
                        elif key == '\x1b[A':  # Up Arrow
                            self.logger.debug("Up arrow key pressed")
                            if self.active_component == 'sidebar':
                                self.sidebar.navigate("up")
                                selected_option = self.sidebar.get_selected_option()
                                if selected_option in ['Home', 'New', 'Top']:
                                    self.current_feed = selected_option.lower()
                                    self.current_screen = 'home'
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
                                if self.user_profile_screen.selected_index > 0:
                                    self.user_profile_screen.selected_index -= 1
                                else:
                                    self.user_profile_screen.scroll_up()
                            elif self.current_screen == 'messages':
                                if self.messages_screen.compose_mode:
                                    if self.messages_screen.current_field == "recipient" and self.messages_screen.cursor_pos > 0:
                                        self.messages_screen.cursor_pos -= 1
                                    elif self.messages_screen.current_field == "subject" and self.messages_screen.cursor_pos > 0:
                                        self.messages_screen.cursor_pos -= 1
                                    elif self.messages_screen.current_field == "message" and self.messages_screen.cursor_pos > 0:
                                        self.messages_screen.cursor_pos -= 1
                                else:
                                    if self.messages_screen.selected_index > 0:
                                        self.messages_screen.selected_index -= 1
                                        if self.messages_screen.scroll_offset > 0:
                                            self.messages_screen.scroll_up()
                        elif key == '\x1b[B':  # Down Arrow
                            self.logger.debug("Down arrow key pressed")
                            if self.active_component == 'sidebar':
                                self.sidebar.navigate("down")
                                selected_option = self.sidebar.get_selected_option()
                                if selected_option in ['Home', 'New', 'Top']:
                                    self.current_feed = selected_option.lower()
                                    self.current_screen = 'home'
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
                                items = self.user_profile_screen.posts if self.user_profile_screen.content_index == 0 else self.user_profile_screen.comments
                                if self.user_profile_screen.selected_index < min(self.user_profile_screen.visible_results - 1, len(items) - self.user_profile_screen.scroll_offset - 1):
                                    self.user_profile_screen.selected_index += 1
                                else:
                                    self.user_profile_screen.scroll_down()
                            elif self.current_screen == 'messages':
                                if self.messages_screen.compose_mode:
                                    if self.messages_screen.current_field == "recipient" and self.messages_screen.cursor_pos < len(self.messages_screen.recipient):
                                        self.messages_screen.cursor_pos += 1
                                    elif self.messages_screen.current_field == "subject" and self.messages_screen.cursor_pos < len(self.messages_screen.subject):
                                        self.messages_screen.cursor_pos += 1
                                    elif self.messages_screen.current_field == "message" and self.messages_screen.cursor_pos < len(self.messages_screen.message_text):
                                        self.messages_screen.cursor_pos += 1
                                else:
                                    if self.messages_screen.selected_index < min(self.messages_screen.visible_messages - 1, len(self.messages_screen.messages) - self.messages_screen.scroll_offset - 1):
                                        self.messages_screen.selected_index += 1
                                        if self.messages_screen.scroll_offset < len(self.messages_screen.messages) - self.messages_screen.visible_messages:
                                            self.messages_screen.scroll_down()
                        elif key == '\x1b[C':  # Right Arrow
                            self.logger.debug("Right arrow key pressed")
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
                            elif self.current_screen == 'profile':
                                self.user_profile_screen.switch_content_type()
                                self.user_profile_screen.load_content()
                            elif self.current_screen == 'messages':
                                if self.messages_screen.compose_mode:
                                    if self.messages_screen.current_field == "recipient" and self.messages_screen.cursor_pos < len(self.messages_screen.recipient):
                                        self.messages_screen.cursor_pos += 1
                                    elif self.messages_screen.current_field == "subject" and self.messages_screen.cursor_pos < len(self.messages_screen.subject):
                                        self.messages_screen.cursor_pos += 1
                                    elif self.messages_screen.current_field == "message" and self.messages_screen.cursor_pos < len(self.messages_screen.message_text):
                                        self.messages_screen.cursor_pos += 1
                                else:
                                    self.messages_screen.next_message()
                        elif key == '\x1b[D':  # Left Arrow
                            self.logger.debug("Left arrow key pressed")
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
                            elif self.current_screen == 'profile':
                                self.user_profile_screen.switch_content_type()
                                self.user_profile_screen.load_content()
                            elif self.current_screen == 'messages':
                                if self.messages_screen.compose_mode:
                                    if self.messages_screen.current_field == "recipient" and self.messages_screen.cursor_pos > 0:
                                        self.messages_screen.cursor_pos -= 1
                                    elif self.messages_screen.current_field == "subject" and self.messages_screen.cursor_pos > 0:
                                        self.messages_screen.cursor_pos -= 1
                                    elif self.messages_screen.current_field == "message" and self.messages_screen.cursor_pos > 0:
                                        self.messages_screen.cursor_pos -= 1
                                else:
                                    self.messages_screen.previous_message()
                        elif key == 'k':  # Upvote
                            self.logger.debug("Upvote key pressed")
                            if self.current_screen == 'post':
                                self.post_view.upvote_post()
                            elif self.current_screen == 'messages' and self.messages_screen.compose_mode:
                                if self.messages_screen.current_field == "recipient":
                                    self.messages_screen.recipient = self.messages_screen.recipient[:self.messages_screen.cursor_pos] + 'k' + self.messages_screen.recipient[self.messages_screen.cursor_pos:]
                                    self.messages_screen.cursor_pos += 1
                                elif self.messages_screen.current_field == "subject":
                                    self.messages_screen.subject = self.messages_screen.subject[:self.messages_screen.cursor_pos] + 'k' + self.messages_screen.subject[self.messages_screen.cursor_pos:]
                                    self.messages_screen.cursor_pos += 1
                                elif self.messages_screen.current_field == "message":
                                    self.messages_screen.message_text = self.messages_screen.message_text[:self.messages_screen.cursor_pos] + 'k' + self.messages_screen.message_text[self.messages_screen.cursor_pos:]
                                    self.messages_screen.cursor_pos += 1
                        elif key == 'j':  # Downvote
                            self.logger.debug("Downvote key pressed")
                            if self.current_screen == 'post':
                                self.post_view.downvote_post()
                            elif self.current_screen == 'messages' and self.messages_screen.compose_mode:
                                if self.messages_screen.current_field == "recipient":
                                    self.messages_screen.recipient = self.messages_screen.recipient[:self.messages_screen.cursor_pos] + 'j' + self.messages_screen.recipient[self.messages_screen.cursor_pos:]
                                    self.messages_screen.cursor_pos += 1
                                elif self.messages_screen.current_field == "subject":
                                    self.messages_screen.subject = self.messages_screen.subject[:self.messages_screen.cursor_pos] + 'j' + self.messages_screen.subject[self.messages_screen.cursor_pos:]
                                    self.messages_screen.cursor_pos += 1
                                elif self.messages_screen.current_field == "message":
                                    self.messages_screen.message_text = self.messages_screen.message_text[:self.messages_screen.cursor_pos] + 'j' + self.messages_screen.message_text[self.messages_screen.cursor_pos:]
                                    self.messages_screen.cursor_pos += 1
                        elif key == '\t':  # Tab
                            self.logger.debug("Tab key pressed")
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
                            elif self.current_screen == "profile":
                                self.user_profile_screen.switch_content_type()
                            elif self.current_screen == 'post':
                                self.post_view.comment_sort_index = (self.post_view.comment_sort_index + 1) % len(self.post_view.comment_sort_options)
                                self.post_view.comment_sort_mode = self.post_view.comment_sort_options[self.post_view.comment_sort_index]
                                if self.post_view.current_post:
                                    comments = self.load_post_comments(self.post_view.current_post)
                                    if self.post_view.comment_sort_mode == "best":
                                        comments.sort(key=lambda x: x.score, reverse=True)
                                    elif self.post_view.comment_sort_mode == "top":
                                        comments.sort(key=lambda x: x.score, reverse=True)
                                    elif self.post_view.comment_sort_mode == "new":
                                        comments.sort(key=lambda x: x.created_utc, reverse=True)
                                    elif self.post_view.comment_sort_mode == "controversial":
                                        comments.sort(key=lambda x: x.controversiality, reverse=True)
                                    self.post_view.comments = comments
                                    self.post_view.comment_lines = []
                                    for comment in self.post_view.comments:
                                        if hasattr(comment, 'body'):
                                            self.post_view.comment_lines.extend(self.post_view.display_comment(comment, 0, self.post_view.content_width))
                                    self.post_view.comment_scroll_offset = 0
                            elif self.current_screen == 'messages' and self.messages_screen.compose_mode:
                                if self.messages_screen.current_field == "recipient":
                                    self.messages_screen.current_field = "subject"
                                    self.messages_screen.cursor_pos = len(self.messages_screen.subject)
                                elif self.messages_screen.current_field == "subject":
                                    self.messages_screen.current_field = "message"
                                    self.messages_screen.cursor_pos = len(self.messages_screen.message_text)
                                else:
                                    self.messages_screen.current_field = "recipient"
                                    self.messages_screen.cursor_pos = len(self.messages_screen.recipient)
                        elif key == '\x7f':  # Backspace
                            self.logger.debug("Backspace key pressed")
                            if self.current_screen == 'search':
                                self.search_screen.backspace()
                            elif self.current_screen == 'post' and self.post_view.comment_mode:
                                if self.post_view.comment_cursor_pos > 0:
                                    self.post_view.comment_text = self.post_view.comment_text[:self.post_view.comment_cursor_pos-1] + self.post_view.comment_text[self.post_view.comment_cursor_pos:]
                                    self.post_view.comment_cursor_pos -= 1
                            elif self.current_screen == 'messages' and self.messages_screen.compose_mode:
                                if self.messages_screen.current_field == "recipient":
                                    if self.messages_screen.cursor_pos > 0:
                                        self.messages_screen.recipient = self.messages_screen.recipient[:self.messages_screen.cursor_pos-1] + self.messages_screen.recipient[self.messages_screen.cursor_pos:]
                                        self.messages_screen.cursor_pos -= 1
                                elif self.messages_screen.current_field == "subject":
                                    if self.messages_screen.cursor_pos > 0:
                                        self.messages_screen.subject = self.messages_screen.subject[:self.messages_screen.cursor_pos-1] + self.messages_screen.subject[self.messages_screen.cursor_pos:]
                                        self.messages_screen.cursor_pos -= 1
                                elif self.messages_screen.current_field == "message":
                                    if self.messages_screen.cursor_pos > 0:
                                        self.messages_screen.message_text = self.messages_screen.message_text[:self.messages_screen.cursor_pos-1] + self.messages_screen.message_text[self.messages_screen.cursor_pos:]
                                        self.messages_screen.cursor_pos -= 1
                        elif len(key) == 1 and key.isprintable():  # Regular character input
                            self.logger.debug(f"Character input: {key}")
                            if self.current_screen == 'search':
                                self.search_screen.add_char(key)
                                self.active_component = 'post_list'
                            elif key.lower() == "o" and self.current_screen == 'post' and not self.post_view.comment_mode:
                                self.post_options_view.current_post = self.post_view.current_post
                                self.current_screen = 'post_options'
                            elif self.current_screen == 'post_options':
                                result = self.post_options_view.handle_input(key)
                                if result in ["reported", "saved", "unsaved"]:
                                    time.sleep(1)
                                    self.current_screen = 'post'
                                    self.post_options_view.confirming_save = False
                                    self.post_options_view.confirming_report = False
                                    self.post_options_view.selected_reason = None
                                    # Refresh the post to update its state
                                    if self.post_view.current_post:
                                        comments = self.load_post_comments(self.post_view.current_post)
                                        self.post_view.display_post(self.post_view.current_post, comments)
                                elif result == "comment":
                                    self.current_screen = 'post'
                                    self.post_view.comment_mode = True
                                    self.post_options_view.confirming_save = False
                                    self.post_options_view.confirming_report = False
                                    self.post_options_view.selected_reason = None
                                elif result and result.startswith("error:"):
                                    time.sleep(1)
                                self.render()
                            elif self.current_screen == 'post' and self.post_view.comment_mode:
                                self.post_view.comment_text = self.post_view.comment_text[:self.post_view.comment_cursor_pos] + key + self.post_view.comment_text[self.post_view.comment_cursor_pos:]
                                self.post_view.comment_cursor_pos += 1
                            elif key == '3' and self.current_screen == 'post':
                                self.post_view.report_post()
                            elif self.current_screen == 'messages' and self.messages_screen.compose_mode:
                                if self.messages_screen.current_field == "recipient":
                                    self.messages_screen.recipient = self.messages_screen.recipient[:self.messages_screen.cursor_pos] + key + self.messages_screen.recipient[self.messages_screen.cursor_pos:]
                                    self.messages_screen.cursor_pos += 1
                                elif self.messages_screen.current_field == "subject":
                                    self.messages_screen.subject = self.messages_screen.subject[:self.messages_screen.cursor_pos] + key + self.messages_screen.subject[self.messages_screen.cursor_pos:]
                                    self.messages_screen.cursor_pos += 1
                                elif self.messages_screen.current_field == "message":
                                    self.messages_screen.message_text = self.messages_screen.message_text[:self.messages_screen.cursor_pos] + key + self.messages_screen.message_text[self.messages_screen.cursor_pos:]
                                    self.messages_screen.cursor_pos += 1
                            elif key.lower() == 'n' and self.current_screen == 'messages' and not self.messages_screen.compose_mode:
                                self.messages_screen.start_compose()
                        elif key in ['\r', '\n', '\x0a', '\x0d', '\x1b\x0d', '\x1b\x0a']:  # Enter
                            self.logger.debug("Enter key pressed")
                            if self.current_screen == 'post' and self.post_view.comment_mode:
                                if self.post_view.comment_text.strip():
                                    try:
                                        self.post_view.current_post.reply(self.post_view.comment_text)
                                        self.post_view.comment_mode = False
                                        self.post_view.comment_text = ""
                                        self.post_view.comment_cursor_pos = 0
                                        # Refresh comments to show the new one
                                        if hasattr(self.post_view.current_post, 'comments'):
                                            self.post_view.current_post.comments.replace_more(limit=0)
                                            self.post_view.comments = list(self.post_view.current_post.comments.list())
                                            self.post_view.comment_lines = []
                                            for comment in self.post_view.comments:
                                                if hasattr(comment, 'body'):
                                                    self.post_view.comment_lines.extend(self.post_view.display_comment(comment, 0, self.post_view.content_width))
                                    except Exception as e:
                                        print(self.term.move(self.term.height - 3, 0) + self.term.red(f"Error submitting comment: {e}"))
                                self.render()
                            elif self.current_screen == 'post_options':
                                result = self.post_options_view.handle_input(key)
                                if result in ["reported", "saved", "unsaved"]:
                                    time.sleep(1)
                                    self.current_screen = 'post'
                                    self.post_options_view.confirming_save = False
                                    self.post_options_view.confirming_report = False
                                    self.post_options_view.selected_reason = None
                                    # Refresh the post to update its state
                                    if self.post_view.current_post:
                                        comments = self.load_post_comments(self.post_view.current_post)
                                        self.post_view.display_post(self.post_view.current_post, comments)
                                elif result == "comment":
                                    self.current_screen = 'post'
                                    self.post_view.comment_mode = True
                                    self.post_options_view.confirming_save = False
                                    self.post_options_view.confirming_report = False
                                    self.post_options_view.selected_reason = None
                                elif result and result.startswith("error:"):
                                    time.sleep(1)
                                self.render()
                            elif self.active_component == 'sidebar':
                                selected_option = self.sidebar.get_selected_option()
                                if selected_option == 'messages':
                                    self.active_component = 'messages'
                                    self.messages_screen.active = True
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
                                if self.settings_screen.theme_screen_activated:
                                    if self.settings_screen.handle_input():
                                        self.current_screen = 'home'
                                        self.active_component = 'sidebar'
                                        self.settings.load_settings_from_file()
                                        self.settings.apply_settings()
                                elif self.settings_screen.handle_enter():
                                    if self.settings_screen.theme_screen_activated:
                                        self.current_screen = 'settings'
                                    else:
                                        self.current_screen = 'home'
                                        self.active_component = 'sidebar'
                                        self.settings.load_settings_from_file()
                                        self.settings.apply_settings()
                                self.sidebar.active = False
                                self.sidebar.selected_index = -1
                                self.post_list.active = False
                                self.active_component = None
                            elif self.current_screen == 'subreddits':
                                selected_subreddit, category = self.subreddits_screen.get_selected_subreddit()
                                if selected_subreddit:
                                    self.current_screen = 'home'
                                    self.active_component = 'post_list'
                                    self.update_posts_from_subreddit(selected_subreddit, category)
                            elif self.current_screen == 'profile':
                                selected_post = self.user_profile_screen.select_item()
                                if selected_post:
                                    comments = self.load_post_comments(selected_post)
                                    self.post_view.display_post(selected_post, comments)
                                    self.post_view.from_search = False
                                    self.current_screen = 'post'
                            elif self.current_screen == 'messages':
                                if self.messages_screen.compose_mode:
                                    if self.messages_screen.current_field == "message":
                                        if self.messages_screen.send_message():
                                            self.messages_screen.compose_mode = False
                                            self.messages_screen.recipient = ""
                                            self.messages_screen.subject = ""
                                            self.messages_screen.message_text = ""
                                            self.messages_screen.cursor_pos = 0
                                            self.messages_screen.current_field = "recipient"
                                            self.messages_screen.load_messages()
                                    elif self.messages_screen.current_field == "recipient":
                                        self.messages_screen.current_field = "subject"
                                        self.messages_screen.cursor_pos = len(self.messages_screen.subject)
                                    elif self.messages_screen.current_field == "subject":
                                        self.messages_screen.current_field = "message"
                                        self.messages_screen.cursor_pos = len(self.messages_screen.message_text)
                                else:
                                    if self.active_component == 'sidebar':
                                        self.active_component = 'messages'
                                    elif self.messages_screen.messages:
                                        selected_message = self.messages_screen.select_message()
                                        if selected_message:
                                            self.messages_screen.start_reply(selected_message)
                    except Exception as e:
                        error_msg = f"Error in main loop: {e}"
                        print(self.term.move(self.term.height - 3, 0) + self.term.red(error_msg))
                        self.logger.error(error_msg, exc_info=True)
                        time.sleep(1)
        except Exception as e:
            error_msg = f"Fatal error: {e}"
            print(self.term.move(self.term.height - 3, 0) + self.term.red(error_msg))
            self.logger.error(error_msg, exc_info=True)
        finally:
            print(self.term.exit_fullscreen())
            self.logger.info("RedditTUI shutdown")

if __name__ == '__main__':
    app = RedditTUI()
    app.run()