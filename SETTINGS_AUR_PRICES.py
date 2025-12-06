# ==============================================================================
#  ⚙️ SETTINGS & CONFIGURATION CENTER (SECURE MODE)
# ==============================================================================

import os
from dotenv import load_dotenv

# .env file load karna
load_dotenv()

# --- 1. SENSITIVE DATA (Loaded from .env) ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

if not BOT_TOKEN or not MONGO_URI:
    print("❌ ERROR: .env file mein Token ya Mongo URI missing hai!")

DB_NAME = "GamingBotDB"

# --- 2. ADMIN PANEL ---
ADMIN_IDS = [
    7000000000,  # Aapki ID (Replace karein)
    987654321    # Client ki ID
]

# --- 3. ECONOMY & PRICES (XP) ---
PRICES = {
    'hint': 50, 'freeze': 75, 'shield': 150,
    'fifty': 60, 'skip': 80, 'double_xp': 100
}

GAME_FEES = {
    'quiz': 20,
    'slots': 50,
    'dice': 100,
    'snake': 10  # New Game Fee
}

# --- 4. SERVER CONFIG ---
# Jab hum online dalenge tab ye URL kaam aayega
WEB_APP_URL = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:5000")