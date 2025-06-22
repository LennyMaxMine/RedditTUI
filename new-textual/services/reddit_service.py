import praw
import os
import json
import time
from pathlib import Path
from utils.logger import Logger
from praw import Reddit
from praw.models import Submission

class RedditService:
    def __init__(self, client_id="", client_secret="", user_agent="RedditTUI/1.0", username=None, password=None):
        self.logger = Logger()
        self.config_dir = Path.home() / ".config" / "reddit-tui"
        self.accounts_file = self.config_dir / "accounts.jhna"
        self.current_account = None
        self.accounts = {}
        self._ensure_config_dir()
        self.user = None
        self.rate_limit_remaining = 600
        self.rate_limit_reset = 0
        self.rate_limit_used = 0
        self.last_request_time = 0
        
        self.accounts = self.load_accounts()
        
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

    def load_accounts(self) -> dict:
        self.logger.info(f"Loading accounts from {self.accounts_file}")
        if self.accounts_file.exists():
            try:
                with open(self.accounts_file, "r") as f:
                    accounts = json.load(f)
                self.logger.info(f"Loaded {len(accounts)} accounts")
                return accounts
            except Exception as e:
                self.logger.error(f"Failed to load accounts: {e}", exc_info=True)
                return {}
        self.logger.info("Accounts file does not exist.")
        return {}

    def save_accounts(self):
        self.logger.info(f"Saving accounts to {self.accounts_file}")
        try:
            with open(self.accounts_file, "w") as f:
                json.dump(self.accounts, f, indent=4)
            self.logger.info("Accounts saved successfully.")
        except Exception as e:
            self.logger.error(f"Failed to save accounts: {e}", exc_info=True)

    def add_account(self, username: str, client_id: str, client_secret: str, password: str) -> bool:
        self.logger.info(f"Adding account: {username}")
        try:
            temp_reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                username=username,
                password=password,
                user_agent="RedditTUI/1.0"
            )
            user = temp_reddit.user.me()
            if user.name != username:
                self.logger.error(f"Username mismatch: expected {username}, got {user.name}")
                return False
            
            self.accounts[username] = {
                "client_id": client_id,
                "client_secret": client_secret,
                "password": password,
                "added_date": time.time(),
                "last_used": time.time()
            }
            self.save_accounts()
            self.logger.info(f"Account {username} added successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add account {username}: {str(e)}", exc_info=True)
            return False

    def remove_account(self, username: str) -> bool:
        self.logger.info(f"Removing account: {username}")
        if username in self.accounts:
            del self.accounts[username]
            self.save_accounts()
            if self.current_account == username:
                self.current_account = None
                self.reddit = None
                self.user = None
            self.logger.info(f"Account {username} removed successfully")
            return True
        return False

    def get_accounts(self) -> list:
        return list(self.accounts.keys())

    def switch_account(self, username: str) -> bool:
        self.logger.info(f"Switching to account: {username}")
        if username not in self.accounts:
            self.logger.error(f"Account {username} not found")
            return False
        
        account_data = self.accounts[username]
        try:
            self.reddit = praw.Reddit(
                client_id=account_data["client_id"],
                client_secret=account_data["client_secret"],
                username=username,
                password=account_data["password"],
                user_agent="RedditTUI/1.0"
            )
            user = self.reddit.user.me()
            self.user = user.name
            self.current_account = username
            self.accounts[username]["last_used"] = time.time()
            self.save_accounts()
            self.logger.info(f"Switched to account: {username}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to switch to account {username}: {str(e)}", exc_info=True)
            return False

    def get_current_account(self) -> str:
        return self.current_account

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
                self.current_account = user.name
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
        self.logger.info(f"Saving credentials for {username}")
        self.accounts[username] = {
            "client_id": client_id,
            "client_secret": client_secret,
            "password": password,
            "added_date": time.time(),
            "last_used": time.time()
        }
        self.save_accounts()

    def load_credentials(self) -> dict:
        self.logger.info("Loading credentials (legacy method)")
        if self.accounts:
            most_recent = max(self.accounts.keys(), key=lambda k: self.accounts[k].get("last_used", 0))
            return self.accounts[most_recent]
        return {}

    def auto_login(self) -> bool:
        self.logger.info("RedditService.auto_login called")
        if not self.accounts:
            self.logger.info("No accounts found for auto-login.")
            return False
        
        most_recent = max(self.accounts.keys(), key=lambda k: self.accounts[k].get("last_used", 0))
        self.logger.info(f"Attempting auto-login with most recent account: {most_recent}")
        return self.switch_account(most_recent)

    def get_hot_posts(self, limit: int = 25):
        if not self.reddit:
            self.logger.error("Cannot get hot posts: Reddit instance not initialized")
            return []
        try:
            self.logger.info(f"Fetching {limit} hot posts from Reddit front page")
            self.logger.info(f"Reddit instance: {self.reddit}")
            self.logger.info(f"Current user: {self.user}")
            self._check_rate_limit()
            response = self.reddit.subreddit("all").hot(limit=limit)
            self.logger.info(f"Reddit API response type: {type(response)}")
            self.logger.info("Reddit API call completed, converting to list")
            posts = list(response)
            self.logger.info(f"Retrieved {len(posts)} hot posts")
            if len(posts) == 0:
                self.logger.warning("No posts retrieved - this might indicate an API issue")a
            self._update_rate_limit(response)
            return posts
        except ConnectionError as e:
            self.logger.error(f"Network connection error getting hot posts: {str(e)}", exc_info=True)
            raise
        except TimeoutError as e:
            self.logger.error(f"Request timeout getting hot posts: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Error getting hot posts: {str(e)}", exc_info=True)
            return []

    def get_new_posts(self, limit: int = 25):
        if not self.reddit:
            self.logger.error("Cannot get new posts: Reddit instance not initialized")
            return []
        try:
            self.logger.info(f"Fetching {limit} new posts from Reddit front page")
            self._check_rate_limit()
            response = self.reddit.subreddit("all").new(limit=limit)
            self.logger.info("Reddit API call completed, converting to list")
            posts = list(response)
            self.logger.info(f"Retrieved {len(posts)} new posts")
            self._update_rate_limit(response)
            return posts
        except ConnectionError as e:
            self.logger.error(f"Network connection error getting new posts: {str(e)}", exc_info=True)
            raise
        except TimeoutError as e:
            self.logger.error(f"Request timeout getting new posts: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Error getting new posts: {str(e)}", exc_info=True)
            return []

    def get_top_posts(self, limit: int = 25):
        if not self.reddit:
            self.logger.error("Cannot get top posts: Reddit instance not initialized")
            return []
        try:
            self.logger.info(f"Fetching {limit} top posts from Reddit front page")
            self._check_rate_limit()
            response = self.reddit.subreddit("all").top(limit=limit)
            self.logger.info("Reddit API call completed, converting to list")
            posts = list(response)
            self.logger.info(f"Retrieved {len(posts)} top posts")
            self._update_rate_limit(response)
            return posts
        except ConnectionError as e:
            self.logger.error(f"Network connection error getting top posts: {str(e)}", exc_info=True)
            raise
        except TimeoutError as e:
            self.logger.error(f"Request timeout getting top posts: {str(e)}", exc_info=True)
            raise
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
        """Subscribe to a subreddit."""
        try:
            if not self.reddit or not self.user:
                return False
            
            subreddit = self.reddit.subreddit(subreddit_name)
            subreddit.subscribe()
            self.logger.info(f"Subscribed to r/{subreddit_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error subscribing to r/{subreddit_name}: {str(e)}", exc_info=True)
            return False

    def unsubscribe_subreddit(self, subreddit_name: str) -> bool:
        """Unsubscribe from a subreddit."""
        try:
            if not self.reddit or not self.user:
                return False
            
            subreddit = self.reddit.subreddit(subreddit_name)
            subreddit.unsubscribe()
            self.logger.info(f"Unsubscribed from r/{subreddit_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error unsubscribing from r/{subreddit_name}: {str(e)}", exc_info=True)
            return False

    def get_subreddit_info(self, subreddit_name: str):
        """Get information about a subreddit."""
        try:
            if not self.reddit:
                return None
            
            subreddit = self.reddit.subreddit(subreddit_name)
            return {
                'display_name': subreddit.display_name,
                'title': subreddit.title,
                'description': subreddit.description,
                'subscribers': subreddit.subscribers,
                'active_user_count': subreddit.active_user_count,
                'created_utc': subreddit.created_utc,
                'over18': subreddit.over18,
                'public_description': subreddit.public_description,
                'url': subreddit.url
            }
        except Exception as e:
            self.logger.error(f"Error getting subreddit info for r/{subreddit_name}: {str(e)}", exc_info=True)
            return None

    def search_subreddits(self, query: str, limit: int = 10):
        """Search for subreddits."""
        try:
            if not self.reddit:
                return []
            
            subreddits = self.reddit.subreddits.search(query, limit=limit)
            return list(subreddits)
        except Exception as e:
            self.logger.error(f"Error searching subreddits: {str(e)}", exc_info=True)
            return []

    def search_users(self, query: str, limit: int = 10):
        """Search for users."""
        try:
            if not self.reddit:
                return []
            
            users = self.reddit.redditors.search(query, limit=limit)
            return list(users)
        except Exception as e:
            self.logger.error(f"Error searching users: {str(e)}", exc_info=True)
            return []

    def vote_comment(self, comment, vote_type: str) -> bool:
        """Vote on a comment (upvote, downvote, or clear vote)."""
        try:
            if not self.reddit or not self.user:
                return False
            
            if vote_type == "upvote":
                comment.upvote()
            elif vote_type == "downvote":
                comment.downvote()
            elif vote_type == "clear":
                comment.clear_vote()
            else:
                return False
            
            self.logger.info(f"Voted on comment {comment.id}: {vote_type}")
            return True
        except Exception as e:
            self.logger.error(f"Error voting on comment: {str(e)}", exc_info=True)
            return False

    def reply_to_comment(self, comment, reply_text: str) -> bool:
        """Reply to a comment."""
        try:
            if not self.reddit or not self.user:
                return False
            
            comment.reply(reply_text)
            self.logger.info(f"Replied to comment {comment.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error replying to comment: {str(e)}", exc_info=True)
            return False

    def edit_comment(self, comment, new_text: str) -> bool:
        """Edit a comment."""
        try:
            if not self.reddit or not self.user:
                return False
            
            comment.edit(new_text)
            self.logger.info(f"Edited comment {comment.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error editing comment: {str(e)}", exc_info=True)
            return False

    def delete_comment(self, comment) -> bool:
        """Delete a comment."""
        try:
            if not self.reddit or not self.user:
                return False
            
            comment.delete()
            self.logger.info(f"Deleted comment {comment.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting comment: {str(e)}", exc_info=True)
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

    def get_trending_subreddits(self, limit: int = 10):
        """Get trending subreddits."""
        try:
            if not self.reddit:
                return []
            
            trending = self.reddit.trending_subreddits()
            return list(trending)[:limit]
        except Exception as e:
            self.logger.error(f"Error getting trending subreddits: {str(e)}", exc_info=True)
            return []

    def get_popular_subreddits(self, limit: int = 25):
        """Get popular subreddits."""
        try:
            if not self.reddit:
                return []
            
            popular = self.reddit.subreddits.popular(limit=limit)
            return list(popular)
        except Exception as e:
            self.logger.error(f"Error getting popular subreddits: {str(e)}", exc_info=True)
            return []

    def get_new_subreddits(self, limit: int = 25):
        """Get new subreddits."""
        try:
            if not self.reddit:
                return []
            
            new_subs = self.reddit.subreddits.new(limit=limit)
            return list(new_subs)
        except Exception as e:
            self.logger.error(f"Error getting new subreddits: {str(e)}", exc_info=True)
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