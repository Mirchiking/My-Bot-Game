import asyncio
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
import DATABASE_MEMORY as db
import SETTINGS_AUR_PRICES as settings

# ... (HINGLISH_DB list same rahegi, usko yahan paste kar lena ya purana rakhna) ...

# --- GAME MENU UPGRADED ---
async def game_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    fees = settings.GAME_FEES
    
    # Dynamic URL for Full Screen Game
    # Agar local chala rahe ho to localhost, warna render ka URL
    site_url = settings.WEB_APP_URL + "/game/snake"

    txt = f"""
🎮 **GAME ZONE (HYBRID)** 🎮
Ab khelo Full Screen Games bhi!

🐍 **Neon Snake** (Full Screen)
🧠 **Hinglish Quiz** (Classic)
🎰 **Slots 777** (Luck)
🎲 **Dice War** (Risk)
    """
    
    keyboard = [
        # --- NEW FULL SCREEN GAME BUTTON ---
        [InlineKeyboardButton("🚀 PLAY NEON SNAKE (Full Screen)", web_app=WebAppInfo(url=site_url))],
        
        [InlineKeyboardButton("🧠 Play Quiz", callback_data='start_quiz')],
        [InlineKeyboardButton("🎰 Spin Slots", callback_data='start_slots')],
        [InlineKeyboardButton("🎲 Roll Dice", callback_data='start_dice')],
        [InlineKeyboardButton("🔙 Main Menu", callback_data='main_menu')]
    ]
    
    try:
        await query.edit_message_text(text=txt, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    except Exception:
        pass

# ... (Baaki Quiz, Slots, Dice functions same rahenge, unhe mat hatana) ...