# Reddit TUI

A Terminal User Interface (TUI) for Reddit built with Textual.

## Features

- Browse Reddit posts (Hot, New, Top)
- View post details and comments
- Search functionality
- User authentication
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

## Development

This project uses Textual for the TUI framework. To learn more about Textual, visit:
https://textual.textualize.io/

## License

MIT License 
