import sys
from blessed import Terminal
from ui.app import RedditTUI

def main():
    app = RedditTUI()
    app.run()

if __name__ == '__main__':
    main()