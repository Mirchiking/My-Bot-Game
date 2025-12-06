# ==============================================================================
#  🚀 HYBRID ENGINE: BOT + WEB SERVER (FINAL FIXED)
# ==============================================================================

import logging
import warnings
import threading
import os
import sys
from flask import Flask, render_template
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# --- FLASK APP (Website for 24/7 & Games) ---
app = Flask(__name__, template_folder='templates')

@app.route('/')
def home():
    return "🤖 BOT IS ONLINE AND RUNNING 24/7!"

@app.route('/game/snake')
def snake_game():
    return render_template('snake.html')

def run_flask():
    app.run(host='0.0.0.0', port=5000)

# --- IMPORT: Humari Files ---
# Agar yahan koi file missing hogi, to Bot yahi ruk jayega aur Error dega
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
    print(f"❌ CRITICAL IMPORT ERROR: {e}")
    print("⚠️ Solution: requirements.txt check karein kya usme ye library hai?")
    sys.exit() # Bot ko yahi rok do taki aage crash na ho

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
    
    if admin.IS_MAINTENANCE_MODE and not admin.is_admin(user_id):
        await query.answer("🚧 Maintenance Mode ON.", show_alert=True); return
    if police.is_banned(user_id):
        await query.answer("🚫 You are BANNED!", show_alert=True); return

    try:
        if data == 'main_menu': await manager.start_command(update, context)
        elif data == 'menu_games': await games.game_menu(update, context)
        elif data == 'start_quiz': await games.start_quiz_logic(update, context)
        elif data == 'start_slots': await games.play_slots(update, context)
        elif data == 'start_dice': await games.play_dice(update, context)
        elif data.startswith('ans|'): await games.check_quiz_answer(update, context)
        elif data.startswith('life|'): await games.use_lifeline(update, context)
        elif data == 'menu_shop': await bank.open_shop_menu(update, context)
        elif data.startswith('shop_buy|'): await bank.handle_shop_buy(update, context)
        elif data == 'menu_bank': await bank.open_bank_menu(update, context)
        elif data.startswith('bank_action|'): await bank.handle_bank_action(update, context)
        elif data == 'admin_dashboard': await admin.open_admin_panel(update, context)
        elif data.startswith('admin_act|'): await admin.handle_admin_buttons(update, context)
        else: await query.answer("⚠️ Unknown Button")

    except Exception as e:
        print(f"❌ Button Error: {e}")
        try: await query.answer("⚠️ Error!") 
        except: pass

async def handle_unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_registering = await manager.handle_registration_input(update, context)
    if is_registering: return
    await update.message.reply_text("🤖 Main commands nahi samajhta. Buttons use karo!")

# ==============================================================================
#  MAIN EXECUTION
# ==============================================================================

if __name__ == '__main__':
    print("🤖 STARTING: Hybrid System...")

    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("🌐 WEB SERVER STARTED (Port 5000)")

    try:
        application = ApplicationBuilder().token(settings.BOT_TOKEN).build()
        
        application.add_handler(CommandHandler('start', manager.start_command))
        application.add_handler(CommandHandler('broadcast', admin.broadcast_msg))
        application.add_handler(CommandHandler('give', admin.give_money))
        application.add_handler(CommandHandler('check', admin.check_user))
        application.add_handler(CommandHandler('maintenance', admin.maintenance_mode))
        application.add_handler(CommandHandler('reset', admin.reset_user_command))
        
        application.add_handler(CallbackQueryHandler(handle_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unknown_text))
        
        print(f"🚀 BOT IS LIVE! Connected to: {settings.DB_NAME}")
        
        # Render Crash Fix
        application.run_polling(allowed_updates=Update.ALL_TYPES, stop_signals=None)
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")