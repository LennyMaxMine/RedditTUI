from blessed import Terminal
import click
import praw
import sys
import tty
import termios
import json
import os
from pathlib import Path

class LoginScreen:
    def __init__(self, reddit_instance=None):
        self.reddit_instance = reddit_instance
        self.term = Terminal()
        self.config_dir = Path.home() / '.reddittui'
        self.config_file = self.config_dir / 'cookies.jhna'
        self.ensure_config_dir()
        self.auto_login()

    def ensure_config_dir(self):
        self.config_dir.mkdir(exist_ok=True)
        if not self.config_file.exists():
            self.config_file.touch()

    def save_credentials(self, client_id, client_secret, username, password):
        config = {
            'client_id': client_id,
            'client_secret': client_secret,
            'username': username,
            'password': password
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f)
        os.chmod(self.config_file, 0o600)

    def load_credentials(self):
        if not self.config_file.exists():
            return None
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except:
            return None

    def auto_login(self):
        saved_creds = self.load_credentials()
        if saved_creds and all(k in saved_creds for k in ['client_id', 'client_secret', 'username', 'password']):
            try:
                self.reddit_instance = praw.Reddit(
                    client_id=saved_creds['client_id'],
                    client_secret=saved_creds['client_secret'],
                    username=saved_creds['username'],
                    password=saved_creds['password'],
                    user_agent='RedditTUI/0.1'
                )
                self.reddit_instance.user.me()
                print(self.term.clear())
                print(self.term.move(0, 0))
                print(self.term.green(f"Auto-login successful! Welcome back, u/{saved_creds['username']}"))
                print(self.term.green("Press Enter to continue..."))
                input()
                return True
            except Exception as e:
                print(self.term.clear())
                print(self.term.move(0, 0))
                print(self.term.yellow(f"Auto-login failed: {str(e)}"))
                print(self.term.yellow("Please log in manually."))
                print(self.term.yellow("Press Enter to continue..."))
                input()
                return False
        return False

    def get_input(self, prompt):
        sys.stdout.write(prompt)
        sys.stdout.flush()
        
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            chars = []
            while True:
                char = sys.stdin.read(1)
                if char == '\x04':  # Ctrl+D
                    break
                if char == '\r' or char == '\n':  # Enter
                    sys.stdout.write('\n')
                    break
                if char == '\x7f':  # Backspace
                    if chars:
                        chars.pop()
                        sys.stdout.write('\b \b')
                else:
                    chars.append(char)
                    sys.stdout.write(char)
                sys.stdout.flush()
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        return ''.join(chars)

    def display(self):
        if self.reddit_instance:
            return

        print(self.term.clear())
        print(self.term.move(0, 0))
        print(self.term.bold("Login to Reddit"))
        print("\nPlease enter your credentials:\n")
        
        saved_creds = self.load_credentials()
        if saved_creds:
            print(self.term.cyan("Found saved credentials. Press Enter to use them or type new ones."))
            print(f"Saved username: {saved_creds['username']}")
            print()
        
        client_id = self.get_input("Client ID: ")
        print()
        if not client_id and saved_creds:
            client_id = saved_creds['client_id']
            print(f"Using saved Client ID: {client_id}")
        
        client_secret = self.get_input("Client Secret: ")
        print()
        if not client_secret and saved_creds:
            client_secret = saved_creds['client_secret']
            print(f"Using saved Client Secret: {client_secret}")
        
        username = self.get_input("Username: ")
        print()
        if not username and saved_creds:
            username = saved_creds['username']
            print(f"Using saved Username: {username}")
        
        password = self.get_input("Password: ")
        print()

        if not all([client_id, client_secret, username, password]):
            print(self.term.red("All fields are required!"))
            return

        self.authenticate(client_id, client_secret, username, password)

    def authenticate(self, client_id, client_secret, username, password):
        try:
            self.reddit_instance = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                username=username,
                password=password,
                user_agent='RedditTUI/0.1'
            )
            self.reddit_instance.user.me()
            print(self.term.green("Login successful!"))
            print(self.term.green(f"Welcome, u/{username}!"))
            self.save_credentials(client_id, client_secret, username, password)
        except Exception as e:
            print(self.term.red(f"Login failed: {str(e)}"))
            self.reddit_instance = None