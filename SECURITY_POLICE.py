import time
from telegram import Bot
import SETTINGS_AUR_PRICES as settings

# ==============================================================================
#  SECURITY & ANTI-CHEAT SYSTEM
#  Ye bot ka Watchman hai.
# ==============================================================================

class SecuritySystem:
    def __init__(self):
        self.spam_record = {}     # User kab click kiya uska time rakhega
        self.blacklist = set()    # Banned users ki list (RAM mein)
        
        # Spam Settings: 1.5 second ka cooldown har click ke beech
        self.COOLDOWN = 1.5 
        
    def get_rank(self, lifetime_xp):
        """
        XP ke hisaab se mathematical Rank Calculation.
        Returns: ('rank_key', 'Display Name')
        """
        if lifetime_xp < 1000:
            return "noob"
        elif lifetime_xp < 5000:
            return "pro"
        elif lifetime_xp < 20000:
            return "legend"
        else:
            return "god"

    def is_spamming(self, user_id):
        """
        Check karta hai ki banda button spam to nahi kar raha.
        True = Spam kar raha hai (Ignore karo)
        False = Sab sahi hai (Process karo)
        """
        current_time = time.time()
        
        # Agar user pehli baar aaya hai
        if user_id not in self.spam_record:
            self.spam_record[user_id] = current_time
            return False
            
        last_time = self.spam_record[user_id]
        
        # Agar cooldown se pehle click kiya
        if current_time - last_time < self.COOLDOWN:
            return True # SPAM DETECTED
        
        # Update time
        self.spam_record[user_id] = current_time
        return False

    def is_banned(self, user_id):
        """Check if user blacklisted hai"""
        return user_id in self.blacklist

    def ban_user(self, user_id):
        """User ko RAM mein block karta hai"""
        self.blacklist.add(user_id)
        print(f"🚫 BANNED USER: {user_id}")

    async def alert_admin(self, bot: Bot, message):
        """
        Seedha Admin (Client) ko message bhejta hai.
        """
        try:
            admin_id = settings.ADMIN_ID
            await bot.send_message(chat_id=admin_id, text=f"🚨 **SECURITY ALERT** 🚨\n\n{message}")
        except Exception as e:
            print(f"❌ Admin Alert Failed: {e}")

    def check_suspicious_activity(self, amount):
        """
        Agar transaction amount bahut bada hai to check karega.
        """
        if amount > 5000: # Agar 5000 se jada ek baar me add hua
            return True, "⚠️ High Value Transaction Detected!"
        if amount < 0: # Negative value hack
            return True, "⚠️ Negative XP Injection Attempt!"
            
        return False, "Safe"

# Global Instance create kar rahe hain taki baki files use kar sakein
police = SecuritySystem()