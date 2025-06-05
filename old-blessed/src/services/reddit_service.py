import praw
import requests

REDDIT_URL = "https://www.reddit.com/.json"

class RedditService:
    def __init__(self, client_id=None, client_secret=None, username=None, password=None):
        self.reddit_instance = None
        if client_id and client_secret and username and password:
            self.login(client_id, client_secret, username, password)

    def login(self, client_id, client_secret, username, password):
        try:
            self.reddit_instance = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                username=username,
                password=password,
                user_agent='RedditTUI/0.1'
            )
            self.reddit_instance.user.me()  # Test the login
            return True
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def fetch_hot_posts(self, limit=5):
        if self.reddit_instance:
            return self.reddit_instance.front.hot(limit=limit)
        else:
            headers = {'User-Agent': 'RedditTUI/0.1'}
            response = requests.get(REDDIT_URL, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data['data']['children'][:limit]

    def fetch_post_details(self, post_id):
        if self.reddit_instance:
            return self.reddit_instance.submission(id=post_id)
        else:
            raise Exception("Not logged in. Cannot fetch post details.")

    def logout(self):
        self.reddit_instance = None