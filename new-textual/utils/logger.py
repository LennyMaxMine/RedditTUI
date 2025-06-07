import logging
import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'textual_tui.log')

class Logger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._setup()
        return cls._instance

    def _setup(self):
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        
        with open(LOG_FILE, "w") as f:
            f.write(f"=== Log started at {datetime.now()} ===\n")
        
        self.logger = logging.getLogger('TextualTUI')
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        
        self.logger.handlers = []
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.info("Logger initialized")

    def info(self, message):
        self.logger.info(message)
        print(f"INFO: {message}")

    def warning(self, message):
        self.logger.warning(message)
        print(f"WARNING: {message}")

    def error(self, message, exc_info=None):
        self.logger.error(message, exc_info=exc_info)
        print(f"ERROR: {message}")

    def debug(self, message):
        self.logger.debug(message)
        print(f"DEBUG: {message}")