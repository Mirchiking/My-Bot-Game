# ==============================================================================
#  🚀 HYBRID ENGINE: BOT + WEB SERVER
# ==============================================================================

import logging
import warnings
import asyncio
import threading
from flask import Flask, render_template
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# --- FLASK APP (Website for 24/7 & Games) ---
app = Flask(__name__, template_folder='templates')

@app.route('/')
def home():
    return "🤖 BOT IS ONLINE AND RUNNING 24/7!"

@app.route('/game/snake')
def snake_game():
    # Ye Neon Snake game ki HTML file kholega
    return render_template('snake.html')

def run_flask():
    # Server ko alag thread me chalana
    app.run(host='0.0.0.0', port=5000)

# --- IMPORT: Humari Files ---
try:
    import SETTINGS_AUR_PRICES as settings
    import DATABASE_MEMORY as db
    import MANAGER_HANDLE as manager
    import BANK_AUR_SHOP as bank
    import ALL_GAMES as games
    import ADMIN_POWER as admin
    from SECURITY_POLICE import police
    print("✅ SYSTEM: Saari files connected.")
except ImportError as e:
    print(f"❌ SYSTEM ERROR: File missing: {e}")
    exit()

# --- LOGGING ---
logging.basicConfig(level=logging.ERROR)
warnings.filterwarnings("ignore")

# ==============================================================================
#  CALLBACK HANDLER
# ==============================================================================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    
    # Basic Checks
    if admin.IS_MAINTENANCE_MODE and not admin.is_admin(user_id):
        await query.answer("🚧 Maintenance Mode ON.", show_alert=True); return
    if police.is_banned(user_id):
        await query.answer("🚫 You are BANNED!", show_alert=True); return

    try:
        if data == 'main_menu': await manager.start_command(update, context)
        elif data == 'menu_games': await games.game_menu(update, context)
        
        # New Web Game Logic handled in ALL_GAMES.py mostly
        
        # Old Routes
        elif data == 'start_quiz': await games.start_quiz_logic(update, context)
        elif data == 'start_slots': await games.play_slots(update, context)
        elif data == 'start_dice': await games.play_dice(update, context)
        elif data.startswith('ans|'): await games.check_quiz_answer(update, context)
        elif data.startswith('life|'): await games.use_lifeline(update, context)
        
        # Shop/Bank
        elif data == 'menu_shop': await bank.open_shop_menu(update, context)
        elif data.startswith('shop_buy|'): await bank.handle_shop_buy(update, context)
        elif data == 'menu_bank': await bank.open_bank_menu(update, context)
        elif data.startswith('bank_action|'): await bank.handle_bank_action(update, context)
        
        else: await query.answer("⚠️ Unknown Button")

    except Exception as e:
        print(f"❌ Button Error: {e}")

# ==============================================================================
#  MAIN EXECUTION
# ==============================================================================

if __name__ == '__main__':
    print("🤖 STARTING: Hybrid System...")

    # 1. Start Web Server in Background (For 24/7 & Games)
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("🌐 WEB SERVER STARTED (Port 5000)")

    # 2. Start Telegram Bot
    try:
        application = ApplicationBuilder().token(settings.BOT_TOKEN).build()
        
        application.add_handler(CommandHandler('start', manager.start_command))
        # Add other commands here as needed from your list
        
        application.add_handler(CallbackQueryHandler(handle_callback))
        # Text handler logic...
        
        print(f"🚀 BOT IS LIVE! Connected to: {settings.DB_NAME}")
        application.run_polling()
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")