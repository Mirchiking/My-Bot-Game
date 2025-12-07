import time
from telegram import Bot
import SETTINGS_AUR_PRICES as settings

class SecuritySystem:
    def __init__(self):
        self.spam_record = {}     
        self.blacklist = set()    
        self.COOLDOWN = 1.0 
        
    def is_spamming(self, user_id):
        current_time = time.time()
        if user_id not in self.spam_record:
            self.spam_record[user_id] = current_time
            return False
        last_time = self.spam_record[user_id]
        if current_time - last_time < self.COOLDOWN:
            return True 
        self.spam_record[user_id] = current_time
        return False

    def is_banned(self, user_id):
        return user_id in self.blacklist

    def ban_user(self, user_id):
        self.blacklist.add(user_id)
        
    def unban_user(self, user_id):
        if user_id in self.blacklist:
            self.blacklist.remove(user_id)

police = SecuritySystem()