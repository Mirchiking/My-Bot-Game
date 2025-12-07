import os
from dotenv import load_dotenv
import pytz

load_dotenv()

# --- 1. SENSITIVE DATA ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "MysteryHuntProDB"

# Web App URL (Must be HTTPS for Telegram WebApps)
WEB_APP_URL = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:5000")

# --- 2. ADMIN CONFIG ---
# Main Owner ID from Environment
try:
    OWNER_ID = int(os.getenv("ADMIN_USER_ID", "0"))
except ValueError:
    OWNER_ID = 0

# List of all Admins
ADMIN_IDS = [OWNER_ID] 

# --- 3. ECONOMY & PRICES ---
REAL_MONEY_RATE = 10.0  # ₹10 = 100 XP

PRICES = {
    'hint': 50,
    'fifty': 50,
    'skip': 50,
    'shield': 50,
    'bowl_ball': 100,
    'horse_min_bet': 50
}

# --- 4. PAYOUTS ---
PAYOUTS = {
    'bowl_jackpot': 90,    # 90x
    'horse_win': 90        # 90x
}

# --- 5. HORSE GAME MARKETS (IST) ---
TIMEZONE = pytz.timezone('Asia/Kolkata')

# Structure: Open(H,M), Close(H,M)
MARKETS = {
    'DISAWAR':   {'open_h': 9,  'open_m': 0,  'close_h': 0,  'close_m': 0},  
    'FARIDABAD': {'open_h': 19, 'open_m': 0,  'close_h': 16, 'close_m': 0}, 
    'GHAZIABAD': {'open_h': 22, 'open_m': 30, 'close_h': 20, 'close_m': 30},
    'GALI':      {'open_h': 0,  'open_m': 0,  'close_h': 22, 'close_m': 20},
    'SG':        {'open_h': 17, 'open_m': 0,  'close_h': 15, 'close_m': 30}
}