import logging
import os
from datetime import datetime

class Logger:
    def __init__(self):
        self.logger = logging.getLogger('RedditTUI')
        self.logger.setLevel(logging.INFO)
        
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        log_file = f'logs/reddit_tui_{datetime.now().strftime("%Y%m%d")}.log'
        with open(log_file, 'w') as f:
            pass
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
    
    def error(self, message, exc_info=None):
        self.logger.error(message, exc_info=exc_info)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def info(self, message):
        self.logger.info(message)
    
    def debug(self, message):
        if self.logger.level <= logging.DEBUG:
            self.logger.debug(message) 