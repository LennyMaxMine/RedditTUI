# RedditTUI

A modern terminal-based Reddit client built with Python and Textual framework. Browse Reddit with a beautiful, keyboard-driven interface.

![Account Management Page](https://media.discordapp.net/attachments/1187850686273159188/1390444680260620550/image.png?ex=686ce544&is=686b93c4&hm=bcd8b946699cfd28f7c4e2fff54c4b0d2072100f4b40cfb157bcf28012f0b0ae&=&format=webp&quality=lossless)
![Home Page](https://media.discordapp.net/attachments/1187850686273159188/1386666396728954961/image.png?ex=686cfe37&is=686bacb7&hm=eabf4292db7977d137112f4114d018cfd7be3360854f7a5a9710654e5a553d81&=&format=webp&quality=lossless&width=1580&height=852)
![Post View Page](https://media.discordapp.net/attachments/1187850686273159188/1386666673507143680/image.png?ex=686cfe79&is=686bacf9&hm=763c08b42b3fc0364715112b3e44fcd576dacee20e12610763be7aeecb9b16d7&=&format=webp&quality=lossless&width=1585&height=852)
![Credits Page](https://media.discordapp.net/attachments/1187850686273159188/1386666744273305700/image.png?ex=686cfe8a&is=686bad0a&hm=c5791a68aadbf6e6a7186401131be01c6cef2d6fda7d013036a029032120a200&=&format=webp&quality=lossless&width=1583&height=852)

## Features

- **Multi-account support** - Switch between multiple Reddit accounts
- **Beautiful UI** - Modern terminal interface with themes
- **Full Reddit functionality** - Browse, post, comment, vote, and search
- **Keyboard-driven** - Complete navigation with keyboard shortcuts
- **Real-time updates** - Live feed updates and notifications

## Installation

- Easiest way -> Go to the release page and download the application for your system.
- Advanced way -> You can also build it yourself using build.sh or build.bat (pls know what you are doing)

## Quick Start

1. **First Launch**: The app will prompt you to set up logging preferences
2. **Login**: If no account is logged in, the login screen will appear automatically
3. **Browse**: Use `h`, `n`, `t` to switch between Hot, New, and Top feeds
4. **Navigate**: Use arrow keys to move between posts, Enter to select
5. **Quit**: Press `q` to exit

## Authentication

RedditTUI requires authentication to access Reddit content. The app will automatically show the login screen if:

- No accounts are configured
- Auto-login fails
- You're not currently logged in

**To login:**
1. Press `l` or the login screen will appear automatically
2. Enter your Reddit API credentials:
   - **Client ID**: From your Reddit app
   - **Client Secret**: From your Reddit app  
   - **Username**: Your Reddit username
   - **Password**: Your Reddit password
3. Press `Enter` to login

**Reddit API Setup:**
1. Go to https://www.reddit.com/prefs/apps
2. Click "create another app..."
3. Fill in the details:
   - Name: TUI
   - Type: script
   - Description: A TUI client for Reddit
   - About URL: (leave blank)
   - Redirect URI: http://localhost:8080
4. Click "create app"
5. Note down the client ID (under the app name) and client secret

## Key Bindings

| Key | Action | Description |
|-----|--------|-------------|
| `h` | Home Feed | View hot posts from front page |
| `n` | New Feed | View newest posts |
| `t` | Top Feed | View top posts |
| `s` | Advanced Search | Search posts with filters |
| `l` | Login | Access login screen |
| `c` | Settings | Configure app preferences |
| `u` | My Profile | View your profile |
| `b` | Saved Posts | View your saved posts |
| `r` | Subscribed Subreddits | Browse your subscriptions |
| `p` | Create Post | Create a new post |
| `m` | Messages | Access private messages |
| `a` | Account Management | Switch between accounts |
| `v` | Subreddit Management | Manage subreddit subscriptions |
| `f` | Search Subreddits | Find new subreddits |
| `g` | Search Users | Search for users |
| `i` | Credits | View app credits |
| `z` | Rate Limit Info | Check API usage |
| `x` | Create Theme | Create custom themes |
| `?` | Help | Show help information |
| `q` | Quit | Exit the application |

## Pages & Screens

### 1. Home Feed (`h`)
**Description**: The main Reddit front page showing hot posts from your subscribed subreddits.

**Tutorial**:
- Press `h` to access the home feed
- Use arrow keys to navigate between posts
- Press `Enter` to view a post in detail
- Press `up/down` to vote on posts
- Press `s` to save a post
- Press `h` to hide a post

### 2. New Feed (`n`)
**Description**: Shows the newest posts from your subscribed subreddits.

**Tutorial**:
- Press `n` to switch to new posts
- Same navigation as home feed
- Posts are sorted by submission time

### 3. Top Feed (`t`)
**Description**: Displays the highest-scoring posts from your subscribed subreddits.

**Tutorial**:
- Press `t` to view top posts
- Posts are sorted by score
- Use same navigation as other feeds

### 4. Advanced Search (`s`)
**Description**: Powerful search interface with multiple filters and options.

**Tutorial**:
- Press `s` to open search screen
- Enter your search query
- Use filters:
  - **Sort by**: Best, Top, New, Controversial
  - **Time**: Hour, Day, Week, Month, Year, All
  - **Type**: Posts, Comments, Subreddits, Users
- Add subreddit filter (e.g., `programming+python`)
- Add author filter for specific users
- Set score and comment thresholds
- Toggle options like NSFW, spoilers, etc.
- Press `Enter` to search

### 5. Login Screen (`l`)
**Description**: Authenticate with Reddit using OAuth credentials. This screen appears automatically when no account is logged in.

**Tutorial**:
- The login screen will appear automatically if you're not authenticated
- Press `l` to manually access login screen
- Enter your Reddit API credentials:
  - **Client ID**: From your Reddit app
  - **Client Secret**: From your Reddit app
  - **Username**: Your Reddit username
  - **Password**: Your Reddit password
- Press `Enter` to login
- Credentials are saved for future use
- After successful login, you'll be redirected to the home feed

### 6. Settings (`c`)
**Description**: Configure app preferences and behavior.

**Tutorial**:
- Press `c` to open settings
- Configure:
  - **Posts per page**: Number of posts to load (10-500)
  - **Comment depth**: How deep to load comment threads (1-100)
  - **Auto load comments**: Automatically load comments when viewing posts
  - **Show NSFW content**: Display NSFW posts
  - **Comment sort**: Default comment sorting method
- Press `Save` to apply changes

### 7. User Profile (`u`)
**Description**: View your own Reddit profile and activity.

**Tutorial**:
- Press `u` to view your profile
- See your karma breakdown
- Browse your posts and comments
- View account statistics
- Access profile actions

### 8. Saved Posts (`b`)
**Description**: Browse posts you've saved on Reddit.

**Tutorial**:
- Press `b` to view saved posts
- Navigate through your saved content
- Use same controls as regular feeds
- Posts are sorted by save date

### 9. Subscribed Subreddits (`r`)
**Description**: Browse and manage your subscribed subreddits.

**Tutorial**:
- Press `r` to view subscriptions
- Use arrow keys to navigate subreddits
- Press `Enter` to view posts from selected subreddit
- See subreddit information and stats

### 10. Create Post (`p`)
**Description**: Create and submit new posts to Reddit.

**Tutorial**:
- Press `p` to create a new post
- Select post type:
  - **Text Post**: Self-post with text content
  - **Link Post**: Link to external content
  - **Image Post**: Upload an image
- Enter subreddit name
- Write your title and content
- Add URL for link/image posts
- Set NSFW/spoiler tags if needed
- Press `Submit` to post

### 11. Messages (`m`)
**Description**: Access and manage private messages and conversations.

**Tutorial**:
- Press `m` to open messages
- View conversations in left panel
- Select conversation to view messages
- Compose new messages
- Search and filter messages
- Mark messages as read/unread

### 12. Account Management (`a`)
**Description**: Manage multiple Reddit accounts and switch between them.

**Tutorial**:
- Press `a` to access account management
- View all saved accounts
- Switch between accounts
- Add new accounts
- Remove existing accounts
- See account login dates

### 13. Subreddit Management (`v`)
**Description**: Discover, subscribe to, and manage subreddits.

**Tutorial**:
- Press `v` to open subreddit management
- Choose view: Subscribed, Popular, New, Trending, Search
- Search for specific subreddits
- Subscribe/unsubscribe from subreddits
- View subreddit information
- Browse subreddit posts

### 14. Search Subreddits (`f`)
**Description**: Find and discover new subreddits.

**Tutorial**:
- Press `f` to search subreddits
- Use advanced search interface
- Filter by category, size, activity
- View subreddit descriptions
- Subscribe to found subreddits

### 15. Search Users (`g`)
**Description**: Search for Reddit users and view their profiles.

**Tutorial**:
- Press `g` to search users
- Enter username or search terms
- View user profiles and activity
- See user statistics and karma
- Access user actions (follow, block, message)

### 16. Credits (`i`)
**Description**: View app credits and acknowledgments.

**Tutorial**:
- Press `i` to view credits
- Read about contributors
- View license information
- See third-party libraries used

### 17. Rate Limit Info (`z`)
**Description**: Monitor Reddit API usage and rate limits.

**Tutorial**:
- Press `z` to view rate limit information
- See current API usage
- Monitor remaining requests
- View reset times
- Get usage recommendations

### 18. Create Theme (`x`)
**Description**: Create custom color themes for the application.

**Tutorial**:
- Press `x` to open theme creator
- Enter theme name
- Customize colors for:
  - Primary, Secondary, Accent
  - Foreground, Background
  - Success, Warning, Error
  - Surface, Panel
- Preview colors in real-time
- Save your custom theme

### 19. Post View Screen
**Description**: Detailed view of a selected post with comments.

**Tutorial**:
- Press `Enter` on any post to view details
- Read full post content
- Browse comments with threading
- Sort comments by: Best, Top, New, Controversial, Old, Q&A
- Vote on comments
- Reply to comments
- Use system commands for additional actions

### 20. Comment Screen
**Description**: Write and submit comments on posts.

**Tutorial**:
- Select a post and choose comment action
- Write your comment in the text area
- Use markdown formatting
- Press `Submit` to post comment
- Press `Cancel` to abort

### 21. QR Code Screen
**Description**: Display QR codes for sharing post URLs.

**Tutorial**:
- Select a post and choose QR code action
- View QR code for post URL
- Scan with mobile device to open in browser
- Press `Close` to return

## System Commands

When viewing posts, additional actions are available through system commands:

- **Back**: Return to post list
- **View User Profile**: View post author's profile
- **Save Post**: Save post to your saved list
- **Hide Post**: Hide post from feeds
- **Subscribe**: Subscribe to post's subreddit
- **Upvote/Downvote**: Vote on posts
- **Report**: Report inappropriate content
- **Comment**: Add a comment
- **Copy URL/Title**: Copy to clipboard
- **Open in Browser**: Open post in default browser
- **Show QR Code**: Display QR code for sharing

## Configuration

Settings are stored in `~/.config/reddit-tui/settings.json`

Account credentials are stored securely in `~/.config/reddit-tui/accounts.jhna`

## Themes

The app includes several built-in themes:
- **Dark**: Default dark theme
- **Light**: Light theme for bright environments
- **Oceanic**: Blue-tinted theme

Create custom themes using the theme creator (`x` key).

## Troubleshooting

**Login Issues**:
- Ensure your Reddit API credentials are correct
- Check that your Reddit app has proper permissions
- Verify your Reddit account is active

**Performance Issues**:
- Reduce posts per page in settings
- Lower comment depth for faster loading
- Check rate limit info for API usage

**Display Issues**:
- Ensure your terminal supports Unicode
- Try different themes for better visibility
- Check terminal color support

## Contributing

This project uses Textual for the TUI framework. To learn more about Textual, visit:
https://textual.textualize.io/

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
