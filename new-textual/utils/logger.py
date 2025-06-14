import logging
import os
import sys
import traceback
import requests
import platform
from datetime import datetime
from pathlib import Path

class Logger:
    _instance = None
    send_logs_to_developer = False
    webhook_url = "https://discord.com/api/webhooks/1383415776081612882/4LzqSGw_T-hc4uxXkguNyk_PGmxm2P0SJF5hnhcpaxULPfQBp9L-lzdpNC3L_TDrmIgO"

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

    def _get_system_info(self):
        return {
            "OS": platform.system(),
            "OS Version": platform.version(),
            "Python Version": platform.python_version(),
            "Architecture": platform.machine(),
            "Processor": platform.processor()
        }

    def _send_log_file(self):
        if not self.send_logs_to_developer:
            return
        try:
            if not self.log_file.exists():
                return
            with open(self.log_file, 'rb') as f:
                log_content = f.read()
            system_info = self._get_system_info()
            info_text = "\n".join(f"{k}: {v}" for k, v in system_info.items())
            
            files = {
                'file': ('textual_tui.log', log_content, 'text/plain')
            }
            payload = {
                "content": f"RedditTUI log file\nSystem Info:\n{info_text}"
            }
        except Exception as e:
            pass

    def _send_crash_report(self, exc_type, exc_value, exc_traceback):
        traceback_text = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        system_info = self._get_system_info()
        embed = {
            "title": "RedditTUI Crash Report",
            "description": f"Crash occurred at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "color": 15158332,
            "fields": [
                {"name": "Exception Type", "value": str(exc_type.__name__), "inline": True},
                {"name": "Exception Message", "value": str(exc_value), "inline": True},
                {"name": "System Information", "value": "\n".join(f"{k}: {v}" for k, v in system_info.items()), "inline": False},
                {"name": "Traceback", "value": f"```\n{traceback_text}\n```"}
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        payload = {"embeds": [embed]}
        response = requests.post(self.webhook_url, json=payload)
        
        try:
            traceback_text = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            system_info = self._get_system_info()
            with open("./logs/crash_report.txt", "w") as f:
                f.write(f"=== Crash Report ===\n")
                f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Exception Type: {exc_type.__name__}\n")
                f.write(f"Exception Message: {str(exc_value)}\n\n")
                f.write(f"=== System Information ===\n")
                for k, v in system_info.items():
                    f.write(f"{k}: {v}\n")
                f.write(f"\n=== Traceback ===\n{traceback_text}\n")
        except Exception:
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

    def send_crash_report(self, exc_type, exc_value, exc_traceback):
        self._send_crash_report(exc_type, exc_value, exc_traceback)