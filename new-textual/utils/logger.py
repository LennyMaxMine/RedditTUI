import logging
import os
import sys
import traceback
import requests
from datetime import datetime
from pathlib import Path

class Logger:
    _instance = None
    send_logs_to_developer = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._setup()
        return cls._instance

    def _setup(self):
        self.logger = logging.getLogger("RedditTUI")
        self.logger.setLevel(logging.DEBUG)

        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        self.log_file = log_dir / "textual_tui.log"

        with open(self.log_file, "w") as f:
            f.write("")

        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.info("Logger initialized")
        self.logger.info("Importing utils package")
        self.logger.info("Importing services package")
        self.logger.info("Importing components package")

        self.webhook_url = "https://discord.com/api/webhooks/1383415776081612882/4LzqSGw_T-hc4uxXkguNyk_PGmxm2P0SJF5hnhcpaxULPfQBp9L-lzdpNC3L_TDrmIgO"

    def _send_log_file(self):
        if not self.send_logs_to_developer:
            return

        try:
            if not self.log_file.exists():
                return

            embed = {
                "title": "RedditTUI Log File",
                "description": f"Log file from {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "color": 3447003,
                "timestamp": datetime.utcnow().isoformat()
            }

            payload = {
                "embeds": [embed]
            }

            files = {
                'file': ('textual_tui.log', open(self.log_file, 'rb'), 'text/plain')
            }

            requests.post(self.webhook_url, json=payload, files=files)
        except:
            pass

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message, exc_info=None):
        self.logger.error(message, exc_info=exc_info)

    def debug(self, message):
        self.logger.debug(message)

    def send_logs(self):
        self._send_log_file()