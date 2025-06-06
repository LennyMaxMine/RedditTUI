import praw
import os
import json
from pathlib import Path

class RedditService:
    def __init__(self):
        self.reddit = None
        self.config_dir = Path.home() / ".config" / "reddit-tui"
        self.credentials_file = self.config_dir / "sanfrancisco.jhna"
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def login(self, client_id: str, client_secret: str, username: str, password: str) -> bool:
        try:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                username=username,
                password=password,
                user_agent="RedditTUI/1.0"
            )
            self.reddit.user.me()
            self._save_credentials(client_id, client_secret, username, password)
            return True
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def _save_credentials(self, client_id: str, client_secret: str, username: str, password: str):
        credentials = {
            "client_id": client_id,
            "client_secret": client_secret,
            "username": username,
            "password": password
        }
        with open(self.credentials_file, "w") as f:
            json.dump(credentials, f)

    def load_credentials(self) -> dict:
        if self.credentials_file.exists():
            with open(self.credentials_file, "r") as f:
                return json.load(f)
        return {}

    def auto_login(self) -> bool:
        credentials = self.load_credentials()
        if all(k in credentials for k in ["client_id", "client_secret", "username", "password"]):
            return self.login(
                credentials["client_id"],
                credentials["client_secret"],
                credentials["username"],
                credentials["password"]
            )
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