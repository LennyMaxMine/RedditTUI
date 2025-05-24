import os
import json

class Settings:
    def __init__(self):
        self.theme = "Default"
        self.posts_per_page = 25
        self.comment_depth = 0
        self.auto_load_comments = True
        self.show_nsfw = True
    
    def load_settings_from_file(self):
        try: 
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as settingsfile:
                    settingsfilejson = json.load(settingsfile)
                    self.theme = settingsfilejson["theme"]
                    self.posts_per_page = int(settingsfilejson["posts_per_page"])
                    self.comment_depth = int(settingsfilejson["comment_depth"])
                    self.auto_load_comments = bool(settingsfilejson["auto_load_comments"])
                    self.show_nsfw = bool(settingsfilejson["show_nsfw"])
        except:
            return("Error, maybe there is no a settings file? Check if there is a settings.json")