import os
from dotenv import load_dotenv
import pytz

load_dotenv()

# --- 1. SENSITIVE DATA ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "MysteryHuntProDB"

# UPI ID
ADMIN_UPI = os.getenv("ADMIN_UPI", "sha.839@ptaxis")

# Web App URL (HTTPS Required)
WEB_APP_URL = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:5000")

# --- 2. ADMIN CONFIG ---
try:
    OWNER_ID = int(os.getenv("ADMIN_USER_ID", "0"))
except ValueError:
    OWNER_ID = 0

# List of Admins (Isme aur IDs comma laga kar add kar sakte ho)
ADMIN_IDS = [OWNER_ID] 

# --- 3. ECONOMY & PRICES ---
PRICES = {
    'hint': 50,
    'shield': 100,
    'fifty': 50,
    'skip': 50,
    'double': 150,
    'snake_fee': 20,
    'slots_fee': 50,
    'dice_fee': 30,
    'quiz_fee': 20,
    'bowl_fee': 100,
    'horse_min_bet': 50
}

# --- 4. PAYOUTS (Multipliers) ---
PAYOUTS = {
    'bowl_jackpot': 90, # 90x
    'horse_win': 90,    # 90x
    'slots_win': 2,     # 2x
    'slots_jackpot': 5, # 5x
    'dice_win': 5,      # 5x
    'snake_per_point': 2 # 2 XP per apple
}

# --- 5. TIME & MARKETS (IST) ---
TIMEZONE = pytz.timezone('Asia/Kolkata')

MARKETS = {
    'DISAWAR':   {'open_h': 9,  'open_m': 0,  'close_h': 0,  'close_m': 0},  
    'FARIDABAD': {'open_h': 19, 'open_m': 0,  'close_h': 16, 'close_m': 0}, 
    'GHAZIABAD': {'open_h': 22, 'open_m': 30, 'close_h': 20, 'close_m': 30},
    'GALI':      {'open_h': 0,  'open_m': 0,  'close_h': 22, 'close_m': 20},
    'SG':        {'open_h': 17, 'open_m': 0,  'close_h': 15, 'close_m': 30}
}