import praw
import os
import json
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
        return list(self.reddit.front.hot(limit=limit))

    def get_new_posts(self, limit: int = 25):
        if not self.reddit:
            return []
        return list(self.reddit.front.new(limit=limit))

    def get_top_posts(self, limit: int = 25):
        if not self.reddit:
            return []
        return list(self.reddit.front.top(limit=limit))

    def get_subreddit_posts(self, subreddit: str, sort: str = "hot", limit: int = 25):
        if not self.reddit:
            return []
        sub = self.reddit.subreddit(subreddit)
        if sort == "hot":
            return list(sub.hot(limit=limit))
        elif sort == "new":
            return list(sub.new(limit=limit))
        elif sort == "top":
            return list(sub.top(limit=limit))
        return list(sub.hot(limit=limit))

    def search_posts(self, query: str, sort: str = "relevance", time_filter: str = "all", limit: int = 25):
        if not self.reddit:
            return []
        try:
            self.logger.info(f"Searching posts with query: {query}, sort: {sort}, time: {time_filter}")
            return list(self.reddit.subreddit("all").search(
                query,
                sort=sort,
                time_filter=time_filter,
                limit=limit
            ))
        except Exception as e:
            self.logger.error(f"Error searching posts: {str(e)}", exc_info=True)
            return []

    def get_post_comments(self, post, sort="best", limit=100):
        try:
            if not self.reddit:
                self.logger.error("Reddit instance not initialized")
                return []

            self.logger.info(f"Getting comments for post: {post.id}")
            post.comments.replace_more(limit=0)
            comments = list(post.comments)
            
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
            return self.reddit.redditor(username)
        except Exception as e:
            self.logger.error(f"Error getting user profile: {str(e)}", exc_info=True)
            return None

    def get_user_posts(self, username: str, limit: int = 25):
        if not self.reddit:
            self.logger.error("Cannot get user posts: Reddit instance not initialized")
            return []
        try:
            user = self.reddit.redditor(username)
            return list(user.submissions.new(limit=limit))
        except Exception as e:
            self.logger.error(f"Error getting user posts: {str(e)}", exc_info=True)
            return []

    def get_user_comments(self, username: str, limit: int = 25):
        if not self.reddit:
            self.logger.error("Cannot get user comments: Reddit instance not initialized")
            return []
        try:
            user = self.reddit.redditor(username)
            return list(user.comments.new(limit=limit))
        except Exception as e:
            self.logger.error(f"Error getting user comments: {str(e)}", exc_info=True)
            return []

    def submit_comment(self, post, body: str) -> bool:
        if not self.reddit:
            self.logger.error("Cannot submit comment: Reddit instance not initialized")
            return False
        try:
            self.logger.info(f"Submitting comment to post: {post.title}")
            comment = post.reply(body)
            self.logger.info(f"Comment submitted successfully: {comment.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error submitting comment: {str(e)}", exc_info=True)
            return False

    def save_post(self, post) -> bool:
        if not self.reddit:
            self.logger.error("Cannot save post: Reddit instance not initialized")
            return False
        try:
            self.logger.info(f"Saving post: {post.title}")
            post.save()
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
            self.logger.info(f"Unsaving post: {post.title}")
            post.unsave()
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
            self.logger.info(f"Hiding post: {post.title}")
            post.hide()
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
            self.logger.info(f"Unhiding post: {post.title}")
            post.unhide()
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
            self.logger.info(f"Subscribing to subreddit: {subreddit_name}")
            self.reddit.subreddit(subreddit_name).subscribe()
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
            self.logger.info(f"Unsubscribing from subreddit: {subreddit_name}")
            self.reddit.subreddit(subreddit_name).unsubscribe()
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
            self.logger.info("Fetching saved posts")
            return list(self.reddit.user.me().saved(limit=limit))
        except Exception as e:
            self.logger.error(f"Error fetching saved posts: {str(e)}", exc_info=True)
            return []

    def get_subscribed_subreddits(self):
        if not self.reddit:
            self.logger.error("Cannot get subscribed subreddits: Reddit instance not initialized")
            return []
        try:
            self.logger.info("Fetching subscribed subreddits")
            return list(self.reddit.user.subreddits())
        except Exception as e:
            self.logger.error(f"Error fetching subscribed subreddits: {str(e)}", exc_info=True)
            return []

    def submit_text_post(self, subreddit, title, content, flair_id=None, nsfw=False, spoiler=False):
        try:
            subreddit_instance = self.reddit.subreddit(subreddit)
            submission = subreddit_instance.submit(
                title=title,
                selftext=content,
                flair_id=flair_id,
                nsfw=nsfw,
                spoiler=spoiler
            )
            self.logger.info(f"Text post submitted successfully to r/{subreddit}")
            return True
        except Exception as e:
            self.logger.error(f"Error submitting text post: {str(e)}", exc_info=True)
            return False

    def submit_link_post(self, subreddit, title, url, flair_id=None, nsfw=False, spoiler=False):
        try:
            subreddit_instance = self.reddit.subreddit(subreddit)
            submission = subreddit_instance.submit(
                title=title,
                url=url,
                flair_id=flair_id,
                nsfw=nsfw,
                spoiler=spoiler
            )
            self.logger.info(f"Link post submitted successfully to r/{subreddit}")
            return True
        except Exception as e:
            self.logger.error(f"Error submitting link post: {str(e)}", exc_info=True)
            return False

    def submit_image_post(self, subreddit, title, image_path, flair_id=None, nsfw=False, spoiler=False):
        try:
            subreddit_instance = self.reddit.subreddit(subreddit)
            with open(image_path, 'rb') as image:
                submission = subreddit_instance.submit_image(
                    title=title,
                    image_path=image_path,
                    flair_id=flair_id,
                    nsfw=nsfw,
                    spoiler=spoiler
                )
            self.logger.info(f"Image post submitted successfully to r/{subreddit}")
            return True
        except Exception as e:
            self.logger.error(f"Error submitting image post: {str(e)}", exc_info=True)
            return False

    def get_subreddit_flairs(self, subreddit):
        try:
            subreddit_instance = self.reddit.subreddit(subreddit)
            return list(subreddit_instance.flair.link_templates)
        except Exception as e:
            self.logger.error(f"Error getting subreddit flairs: {str(e)}", exc_info=True)
            return []