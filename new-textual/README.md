# Reddit TUI

A Terminal User Interface (TUI) for Reddit built with Textual.

## Features

- Browse Reddit posts (Hot, New, Top)
- View post details and comments
- Search functionality
- User authentication
- **Multi-account support** - Switch between multiple Reddit accounts
- Customizable settings

## Installation

1. Clone the repository:
```bash
git clone https://github.com/lennymaxmine/RedditTUI
cd RedditTUI
cd new-textual
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: \venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

## Reddit API Setup

To use this application, you need to create a Reddit application:

1. Go to https://www.reddit.com/prefs/apps
2. Click "create another app..."
3. Fill in the details:
   - Name: TUI
   - Type: script
   - Description: A TUI client
   - About URL: (leave blank)
   - Redirect URI: http://localhost:8080
4. Click "create app"
5. Note down the client ID (under the app name) and client secret

## Usage

Run the application:
```
python main.py
```

### Key Bindings

- `q`: Quit
- `h`: Home feed
- `l`: Login
- `a`: Account Management (add/remove/switch accounts)

### Multi-Account Support

RedditTUI now supports multiple Reddit accounts:

1. **Add Account**: Press `a` to open Account Management, then "Add Account"
2. **Switch Account**: Press `a` and select an account to switch to
3. **Remove Account**: Press `a` and select an account to remove
4. **Auto-login**: The app will automatically log in with your most recently used account

Each account's credentials are securely stored locally and the app remembers which account you last used.

## Development

This project uses Textual for the TUI framework. To learn more about Textual, visit:
https://textual.textualize.io/

## License

MIT License 
