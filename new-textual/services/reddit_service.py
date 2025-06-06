import praw
import os
import json
from pathlib import Path
from utils.logger import Logger

class RedditService:
    def __init__(self):
        self.reddit = None
        self.logger = Logger()
        self.config_dir = Path.home() / ".config" / "reddit-tui"
        self.credentials_file = self.config_dir / "sanfrancisco.jhna"
        self._ensure_config_dir()

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

    def search_posts(self, query: str, limit: int = 25):
        if not self.reddit:
            return []
        return list(self.reddit.subreddit("all").search(query, limit=limit))

    def get_post_comments(self, post_id: str, limit: int = 100):
        if not self.reddit:
            return []
        post = self.reddit.submission(id=post_id)
        post.comments.replace_more(limit=0)
        return list(post.comments.list()[:limit]) 