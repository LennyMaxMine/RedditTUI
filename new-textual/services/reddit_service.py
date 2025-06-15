import praw
import os
import json
import time
from pathlib import Path
from utils.logger import Logger
from praw import Reddit
from praw.models import Submission

class RedditService:
    def __init__(self, client_id, client_secret, user_agent, username=None, password=None):
        self.logger = Logger()
        self.config_dir = Path.home() / ".config" / "reddit-tui"
        self.credentials_file = self.config_dir / "sanfrancisco.jhna"
        self._ensure_config_dir()
        self.user = None
        self.rate_limit_remaining = 600
        self.rate_limit_reset = 0
        self.rate_limit_used = 0
        self.last_request_time = 0
        
        if client_id and client_secret:
            self.reddit = Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent,
                username=username,
                password=password
            )
            self.logger.info("RedditService initialized with provided credentials")
        else:
            self.reddit = None
            self.logger.info("RedditService initialized without credentials")

    def _ensure_config_dir(self):
        self.logger.info(f"Ensuring config dir: {self.config_dir}")
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def login(self, client_id: str, client_secret: str, username: str, password: str) -> bool:
        self.logger.info("RedditService.login called")
        try:
            self.logger.info("Initializing Reddit instance")
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                username=username,
                password=password,
                user_agent="RedditTUI/1.0"
            )
            self.logger.info("Attempting to authenticate with Reddit API...")
            try:
                user = self.reddit.user.me()
                self.user = user.name
                self.logger.info(f"Reddit authentication successful. Logged in as: {user.name}")
                self.logger.info("Saving credentials...")
                self._save_credentials(client_id, client_secret, username, password)
                self.logger.info("Credentials saved successfully.")
                return True
            except Exception as e:
                self.logger.error(f"Reddit API authentication failed: {str(e)}", exc_info=True)
                return False
        except Exception as e:
            self.logger.error(f"Failed to initialize Reddit instance: {str(e)}", exc_info=True)
            return False

    def _save_credentials(self, client_id: str, client_secret: str, username: str, password: str):
        self.logger.info(f"Saving credentials to {self.credentials_file}")
        credentials = {
            "client_id": client_id,
            "client_secret": client_secret,
            "username": username,
            "password": password
        }
        try:
            with open(self.credentials_file, "w") as f:
                json.dump(credentials, f)
            self.logger.info("Credentials file written successfully.")
        except Exception as e:
            self.logger.error(f"Failed to write credentials file: {e}", exc_info=True)

    def load_credentials(self) -> dict:
        self.logger.info(f"Loading credentials from {self.credentials_file}")
        if self.credentials_file.exists():
            try:
                with open(self.credentials_file, "r") as f:
                    creds = json.load(f)
                self.logger.info("Credentials loaded.")
                return creds
            except Exception as e:
                self.logger.error(f"Failed to load credentials: {e}", exc_info=True)
                return {}
        self.logger.info("Credentials file does not exist.")
        return {}

    def auto_login(self) -> bool:
        self.logger.info("RedditService.auto_login called")
        credentials = self.load_credentials()
        if all(k in credentials for k in ["client_id", "client_secret", "username", "password"]):
            self.logger.info("Credentials found, attempting auto-login...")
            return self.login(
                credentials["client_id"],
                credentials["client_secret"],
                credentials["username"],
                credentials["password"]
            )
        self.logger.info("No valid credentials found for auto-login.")
        return False

    def get_hot_posts(self, limit: int = 25):
        if not self.reddit:
            return []
        try:
            self._check_rate_limit()
            response = self.reddit.front.hot(limit=limit)
            posts = list(response)
            self._update_rate_limit(response)
            return posts
        except Exception as e:
            self.logger.error(f"Error getting hot posts: {str(e)}", exc_info=True)
            return []

    def get_new_posts(self, limit: int = 25):
        if not self.reddit:
            return []
        try:
            self._check_rate_limit()
            response = self.reddit.front.new(limit=limit)
            posts = list(response)
            self._update_rate_limit(response)
            return posts
        except Exception as e:
            self.logger.error(f"Error getting new posts: {str(e)}", exc_info=True)
            return []

    def get_top_posts(self, limit: int = 25):
        if not self.reddit:
            return []
        try:
            self._check_rate_limit()
            response = self.reddit.front.top(limit=limit)
            posts = list(response)
            self._update_rate_limit(response)
            return posts
        except Exception as e:
            self.logger.error(f"Error getting top posts: {str(e)}", exc_info=True)
            return []

    def get_subreddit_posts(self, subreddit: str, sort: str = "hot", limit: int = 25):
        if not self.reddit:
            return []
        try:
            self._check_rate_limit()
            sub = self.reddit.subreddit(subreddit)
            if sort == "hot":
                response = sub.hot(limit=limit)
            elif sort == "new":
                response = sub.new(limit=limit)
            elif sort == "top":
                response = sub.top(limit=limit)
            else:
                response = sub.hot(limit=limit)
            posts = list(response)
            self._update_rate_limit(response)
            return posts
        except Exception as e:
            self.logger.error(f"Error getting subreddit posts: {str(e)}", exc_info=True)
            return []

    def search_posts(self, query: str, sort: str = "relevance", time_filter: str = "all", limit: int = 25):
        if not self.reddit:
            return []
        try:
            self._check_rate_limit()
            self.logger.info(f"Searching posts with query: {query}, sort: {sort}, time: {time_filter}")
            response = self.reddit.subreddit("all").search(
                query,
                sort=sort,
                time_filter=time_filter,
                limit=limit
            )
            posts = list(response)
            self._update_rate_limit(response)
            return posts
        except Exception as e:
            self.logger.error(f"Error searching posts: {str(e)}", exc_info=True)
            return []

    def get_post_comments(self, post, sort="best", limit=100):
        try:
            if not self.reddit:
                self.logger.error("Reddit instance not initialized")
                return []

            self._check_rate_limit()
            self.logger.info(f"Getting comments for post: {post.id}")
            post.comments.replace_more(limit=0)
            comments = list(post.comments)
            self._update_rate_limit(post.comments)
            
            if sort == "best":
                comments.sort(key=lambda x: x.score, reverse=True)
            elif sort == "top":
                comments.sort(key=lambda x: x.score, reverse=True)
            elif sort == "new":
                comments.sort(key=lambda x: x.created_utc, reverse=True)
            elif sort == "controversial":
                comments.sort(key=lambda x: abs(x.score), reverse=True)
            elif sort == "old":
                comments.sort(key=lambda x: x.created_utc)
            elif sort == "qa":
                comments.sort(key=lambda x: x.score, reverse=True)
            
            self.logger.info(f"Retrieved {len(comments)} comments")
            return comments[:limit]
        except Exception as e:
            self.logger.error(f"Error getting comments: {str(e)}", exc_info=True)
            return []

    def get_user_profile(self, username: str):
        if not self.reddit:
            self.logger.error("Cannot get user profile: Reddit instance not initialized")
            return None
        try:
            self._check_rate_limit()
            response = self.reddit.redditor(username)
            self._update_rate_limit(response)
            return response
        except Exception as e:
            self.logger.error(f"Error getting user profile: {str(e)}", exc_info=True)
            return None

    def get_user_posts(self, username: str, limit: int = 25):
        if not self.reddit:
            self.logger.error("Cannot get user posts: Reddit instance not initialized")
            return []
        try:
            self._check_rate_limit()
            user = self.reddit.redditor(username)
            response = user.submissions.new(limit=limit)
            posts = list(response)
            self._update_rate_limit(response)
            return posts
        except Exception as e:
            self.logger.error(f"Error getting user posts: {str(e)}", exc_info=True)
            return []

    def get_user_comments(self, username: str, limit: int = 25):
        if not self.reddit:
            self.logger.error("Cannot get user comments: Reddit instance not initialized")
            return []
        try:
            self._check_rate_limit()
            user = self.reddit.redditor(username)
            response = user.comments.new(limit=limit)
            comments = list(response)
            self._update_rate_limit(response)
            return comments
        except Exception as e:
            self.logger.error(f"Error getting user comments: {str(e)}", exc_info=True)
            return []

    def submit_comment(self, post, body: str) -> bool:
        if not self.reddit:
            self.logger.error("Cannot submit comment: Reddit instance not initialized")
            return False
        try:
            self._check_rate_limit()
            self.logger.info(f"Submitting comment to post: {post.title}")
            response = post.reply(body)
            self._update_rate_limit(response)
            self.logger.info(f"Comment submitted successfully: {response.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error submitting comment: {str(e)}", exc_info=True)
            return False

    def save_post(self, post) -> bool:
        if not self.reddit:
            self.logger.error("Cannot save post: Reddit instance not initialized")
            return False
        try:
            self._check_rate_limit()
            self.logger.info(f"Saving post: {post.title}")
            response = post.save()
            self._update_rate_limit(response)
            self.logger.info("Post saved successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error saving post: {str(e)}", exc_info=True)
            return False

    def unsave_post(self, post) -> bool:
        if not self.reddit:
            self.logger.error("Cannot unsave post: Reddit instance not initialized")
            return False
        try:
            self._check_rate_limit()
            self.logger.info(f"Unsaving post: {post.title}")
            response = post.unsave()
            self._update_rate_limit(response)
            self.logger.info("Post unsaved successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error unsaving post: {str(e)}", exc_info=True)
            return False

    def hide_post(self, post) -> bool:
        if not self.reddit:
            self.logger.error("Cannot hide post: Reddit instance not initialized")
            return False
        try:
            self._check_rate_limit()
            self.logger.info(f"Hiding post: {post.title}")
            response = post.hide()
            self._update_rate_limit(response)
            self.logger.info("Post hidden successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error hiding post: {str(e)}", exc_info=True)
            return False

    def unhide_post(self, post) -> bool:
        if not self.reddit:
            self.logger.error("Cannot unhide post: Reddit instance not initialized")
            return False
        try:
            self._check_rate_limit()
            self.logger.info(f"Unhiding post: {post.title}")
            response = post.unhide()
            self._update_rate_limit(response)
            self.logger.info("Post unhidden successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error unhiding post: {str(e)}", exc_info=True)
            return False

    def subscribe_subreddit(self, subreddit_name: str) -> bool:
        if not self.reddit:
            self.logger.error("Cannot subscribe: Reddit instance not initialized")
            return False
        try:
            self._check_rate_limit()
            self.logger.info(f"Subscribing to subreddit: {subreddit_name}")
            subreddit = self.reddit.subreddit(subreddit_name)
            response = subreddit.subscribe()
            self._update_rate_limit(response)
            self.logger.info("Subscribed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error subscribing to subreddit: {str(e)}", exc_info=True)
            return False

    def unsubscribe_subreddit(self, subreddit_name: str) -> bool:
        if not self.reddit:
            self.logger.error("Cannot unsubscribe: Reddit instance not initialized")
            return False
        try:
            self._check_rate_limit()
            self.logger.info(f"Unsubscribing from subreddit: {subreddit_name}")
            subreddit = self.reddit.subreddit(subreddit_name)
            response = subreddit.unsubscribe()
            self._update_rate_limit(response)
            self.logger.info("Unsubscribed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error unsubscribing from subreddit: {str(e)}", exc_info=True)
            return False

    def get_saved_posts(self, limit: int = 25):
        if not self.reddit:
            self.logger.error("Cannot get saved posts: Reddit instance not initialized")
            return []
        try:
            self._check_rate_limit()
            self.logger.info("Fetching saved posts")
            response = self.reddit.user.me().saved(limit=limit)
            posts = list(response)
            self._update_rate_limit(response)
            return posts
        except Exception as e:
            self.logger.error(f"Error fetching saved posts: {str(e)}", exc_info=True)
            return []

    def get_subscribed_subreddits(self):
        if not self.reddit:
            self.logger.error("Cannot get subscribed subreddits: Reddit instance not initialized")
            return []
        try:
            self._check_rate_limit()
            self.logger.info("Fetching subscribed subreddits")
            response = self.reddit.user.subreddits()
            subs = list(response)
            self._update_rate_limit(response)
            return subs
        except Exception as e:
            self.logger.error(f"Error fetching subscribed subreddits: {str(e)}", exc_info=True)
            return []

    def submit_text_post(self, subreddit, title, content, flair_id=None, nsfw=False, spoiler=False):
        try:
            self._check_rate_limit()
            subreddit_instance = self.reddit.subreddit(subreddit)
            response = subreddit_instance.submit(
                title=title,
                selftext=content,
                flair_id=flair_id,
                nsfw=nsfw,
                spoiler=spoiler
            )
            self._update_rate_limit(response)
            self.logger.info(f"Text post submitted successfully to r/{subreddit}")
            return True
        except Exception as e:
            self.logger.error(f"Error submitting text post: {str(e)}", exc_info=True)
            return False

    def submit_link_post(self, subreddit, title, url, flair_id=None, nsfw=False, spoiler=False):
        try:
            self._check_rate_limit()
            subreddit_instance = self.reddit.subreddit(subreddit)
            response = subreddit_instance.submit(
                title=title,
                url=url,
                flair_id=flair_id,
                nsfw=nsfw,
                spoiler=spoiler
            )
            self._update_rate_limit(response)
            self.logger.info(f"Link post submitted successfully to r/{subreddit}")
            return True
        except Exception as e:
            self.logger.error(f"Error submitting link post: {str(e)}", exc_info=True)
            return False

    def submit_image_post(self, subreddit, title, image_path, flair_id=None, nsfw=False, spoiler=False):
        try:
            self._check_rate_limit()
            subreddit_instance = self.reddit.subreddit(subreddit)
            response = subreddit_instance.submit_image(
                title=title,
                image_path=image_path,
                flair_id=flair_id,
                nsfw=nsfw,
                spoiler=spoiler
            )
            self._update_rate_limit(response)
            self.logger.info(f"Image post submitted successfully to r/{subreddit}")
            return True
        except Exception as e:
            self.logger.error(f"Error submitting image post: {str(e)}", exc_info=True)
            return False

    def get_subreddit_flairs(self, subreddit):
        if not self.reddit:
            self.logger.error("Cannot get subreddit flairs: Reddit instance not initialized")
            return []
        try:
            self._check_rate_limit()
            subreddit_instance = self.reddit.subreddit(subreddit)
            response = subreddit_instance.flair.link_templates
            self._update_rate_limit(response)
            return list(response)
        except Exception as e:
            self.logger.error(f"Error getting subreddit flairs: {str(e)}", exc_info=True)
            return []

    def _update_rate_limit(self, response):
        try:
            if hasattr(response, '_response'):
                headers = response._response.headers
                self.logger.info(f"Rate limit headers: {headers}")
                self.rate_limit_remaining = int(float(headers.get('x-ratelimit-remaining', self.rate_limit_remaining)))
                self.rate_limit_reset = int(float(headers.get('x-ratelimit-reset', self.rate_limit_reset)))
                self.rate_limit_used = int(float(headers.get('x-ratelimit-used', self.rate_limit_used)))
                self.last_request_time = time.time()
                self.logger.info(f"Rate limit updated - Remaining: {self.rate_limit_remaining}, Reset: {self.rate_limit_reset}, Used: {self.rate_limit_used}")
        except Exception as e:
            self.logger.error(f"Error updating rate limit: {str(e)}", exc_info=True)

    def get_rate_limit_info(self):
        try:
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            time_until_reset = max(0, self.rate_limit_reset - time_since_last_request)
            
            return {
                'remaining': self.rate_limit_remaining,
                'used': self.rate_limit_used,
                'time_until_reset': time_until_reset,
                'last_request': self.last_request_time
            }
        except Exception as e:
            self.logger.error(f"Error getting rate limit info: {str(e)}", exc_info=True)
            return {
                'remaining': 0,
                'used': 0,
                'time_until_reset': 0,
                'last_request': 0
            }

    def _check_rate_limit(self):
        if self.rate_limit_remaining <= 0:
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            if time_since_last_request < self.rate_limit_reset:
                raise Exception(f"Rate limit exceeded. Please wait {int(self.rate_limit_reset - time_since_last_request)} seconds.")

    def block_user(self, username: str) -> bool:
        if not self.reddit:
            self.logger.error("Cannot block user: Reddit instance not initialized")
            return False
        try:
            self._check_rate_limit()
            self.logger.info(f"Blocking user: {username}")
            self.reddit.redditor(username).block()
            self.logger.info("User blocked successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error blocking user: {str(e)}", exc_info=True)
            return False

    def unblock_user(self, username: str) -> bool:
        if not self.reddit:
            self.logger.error("Cannot unblock user: Reddit instance not initialized")
            return False
        try:
            self._check_rate_limit()
            self.logger.info(f"Unblocking user: {username}")
            self.reddit.redditor(username).unblock()
            self.logger.info("User unblocked successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error unblocking user: {str(e)}", exc_info=True)
            return False

    def follow_user(self, username: str) -> bool:
        if not self.reddit:
            self.logger.error("Cannot follow user: Reddit instance not initialized")
            return False
        try:
            self._check_rate_limit()
            self.logger.info(f"Following user: {username}")
            self.reddit.redditor(username).friend()
            self.logger.info("User followed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error following user: {str(e)}", exc_info=True)
            return False

    def unfollow_user(self, username: str) -> bool:
        if not self.reddit:
            self.logger.error("Cannot unfollow user: Reddit instance not initialized")
            return False
        try:
            self._check_rate_limit()
            self.logger.info(f"Unfollowing user: {username}")
            self.reddit.redditor(username).unfriend()
            self.logger.info("User unfollowed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error unfollowing user: {str(e)}", exc_info=True)
            return False

    def get_followed_users(self):
        if not self.reddit:
            self.logger.error("Cannot get followed users: Reddit instance not initialized")
            return []
        try:
            self._check_rate_limit()
            self.logger.info("Fetching followed users")
            friends = list(self.reddit.user.friends())
            self._update_rate_limit(friends)
            return friends
        except Exception as e:
            self.logger.error(f"Error fetching followed users: {str(e)}", exc_info=True)
            return []

    def get_blocked_users(self):
        if not self.reddit:
            self.logger.error("Cannot get blocked users: Reddit instance not initialized")
            return []
        try:
            self._check_rate_limit()
            self.logger.info("Fetching blocked users")
            blocked = list(self.reddit.user.blocked())
            self._update_rate_limit(blocked)
            return blocked
        except Exception as e:
            self.logger.error(f"Error fetching blocked users: {str(e)}", exc_info=True)
            return []

    def get_messages(self, limit: int = 25):
        if not self.reddit:
            self.logger.error("Cannot get messages: Reddit instance not initialized")
            return []
        try:
            self._check_rate_limit()
            self.logger.info("Fetching messages")
            messages = list(self.reddit.inbox.messages(limit=limit))
            self._update_rate_limit(messages)
            return messages
        except Exception as e:
            self.logger.error(f"Error fetching messages: {str(e)}", exc_info=True)
            return []

    def send_message(self, username: str, subject: str, message: str) -> bool:
        if not self.reddit:
            self.logger.error("Cannot send message: Reddit instance not initialized")
            return False
        try:
            self._check_rate_limit()
            self.logger.info(f"Sending message to {username}")
            self.reddit.redditor(username).message(subject, message)
            self.logger.info("Message sent successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error sending message: {str(e)}", exc_info=True)
            return False

    def mark_message_read(self, message) -> bool:
        if not self.reddit:
            self.logger.error("Cannot mark message as read: Reddit instance not initialized")
            return False
        try:
            self._check_rate_limit()
            self.logger.info(f"Marking message as read: {message.id}")
            message.mark_read()
            self.logger.info("Message marked as read successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error marking message as read: {str(e)}", exc_info=True)
            return False

    def mark_message_unread(self, message) -> bool:
        if not self.reddit:
            self.logger.error("Cannot mark message as unread: Reddit instance not initialized")
            return False
        try:
            self._check_rate_limit()
            self.logger.info(f"Marking message as unread: {message.id}")
            message.mark_unread()
            self.logger.info("Message marked as unread successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error marking message as unread: {str(e)}", exc_info=True)
            return False