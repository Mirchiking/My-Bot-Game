import threading
import sys
import logging
import json
import requests
import os
from flask import Flask, render_template, request, jsonify
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
    MessageHandler, ContextTypes, filters
)

# --- INTERNAL MODULES ---
import SETTINGS_AUR_PRICES as settings
import DATABASE_MEMORY as db
import MANAGER_HANDLE as manager
import ALL_GAMES as games
import ADMIN_POWER as admin
import BANK_AUR_SHOP as bank

# --- LOGGING ---
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ==============================================================================
#  🌐 FLASK WEB SERVER
# ==============================================================================
app = Flask(__name__)

def send_telegram_alert(chat_id, message):
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload)
    except Exception as e: print(f"⚠️ Alert Failed: {e}")

@app.route('/')
def home(): return "🤖 MYSTERY HUNT SERVER IS RUNNING"

# Standard Games
@app.route('/game/snake')
def snake(): return render_template('snake.html') 
@app.route('/game/slots')
def slots(): return render_template('slots.html')
@app.route('/game/dice')
def dice(): return render_template('dice.html')
@app.route('/game/quiz')
def quiz(): return render_template('quiz.html')
# Premium
@app.route('/premium/bowl')
def bowl(): return render_template('bowl.html')
@app.route('/premium/horse')
def horse(): return render_template('horse.html')

@app.route('/api/deduct_fee', methods=['POST'])
def api_deduct():
    try:
        data = request.json
        user_id = int(data.get('user_id'))
        amount = int(data.get('amount'))
        game_name = data.get('game_name')

        user = db.get_user(user_id, "")
        if not user: return jsonify({"status": "fail", "message": "User not found"})

        if user['xp'] >= amount:
            db.update_user(user_id, None, inc_dict={"xp": -amount}, transaction=f"Played {game_name}")
            return jsonify({"status": "success", "new_balance": user['xp'] - amount})
        else:
            return jsonify({"status": "fail", "message": "Insufficient Balance"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/claim_win', methods=['POST'])
def api_claim():
    try:
        data = request.json
        user_id = int(data.get('user_id'))
        amount = int(data.get('amount'))
        game_name = data.get('game_name')

        user = db.get_user(user_id, "")
        loan = user.get('loan_amount', 0)
        
        final_payout = amount
        deducted_loan = 0
        
        if loan > 0:
            if amount >= loan:
                deducted_loan = loan
                final_payout = amount - loan
                db.update_user(user_id, {"loan_amount": 0}, inc_dict={"xp": -loan}, transaction="Loan Auto-Paid")
            else:
                deducted_loan = amount
                final_payout = 0
                db.update_user(user_id, None, inc_dict={"loan_amount": -deducted_loan, "xp": -deducted_loan})

        db.update_user(user_id, None, inc_dict={"xp": amount, "stats.wins": 1}, transaction=f"Won {game_name}")
        
        msg_user = f"🎉 **YOU WON IN {game_name}!**\n💰 Won: {amount} XP"
        if deducted_loan > 0: msg_user += f"\n📉 Loan Paid: -{deducted_loan}"
        msg_user += f"\n💵 **Net Added:** {final_payout} XP"
        
        send_telegram_alert(user_id, msg_user)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ==============================================================================
#  🤖 TELEGRAM BOT LOGIC
# ==============================================================================

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == 'main_menu': await manager.start_command(update, context)
    elif data == 'show_profile': await manager.show_profile(update, context)
    
    elif data == 'menu_games': await games.game_menu(update, context)
    elif data == 'menu_bowl': await games.menu_bowl(update, context)
    elif data == 'menu_horse': await games.menu_horse(update, context)
    
    elif data == 'menu_shop': await bank.open_shop_menu(update, context)
    elif data.startswith('shop_buy|') or data == 'show_upi': await bank.handle_shop_buy(update, context)
    
    elif data == 'menu_bank': await bank.open_bank_menu(update, context)
    elif data.startswith('bank_act|'): await bank.handle_bank_action(update, context)
    
    elif data == 'admin_dashboard': await admin.open_admin_panel(update, context)
    elif data.startswith('admin_act|') or data.startswith('admin_ask|'): await admin.handle_admin_buttons(update, context)
    elif data.startswith('admin_res|'): await admin.handle_market_selection(update, context)
    
    elif data.startswith('reg_gender|'): await manager.handle_gender_selection(update, context)
    else: await query.answer("⚠️ Unknown Action")

async def handle_unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # WebApp Data
    if update.effective_message.web_app_data:
        data = update.effective_message.web_app_data.data
        if data.startswith("bet_horse"):
            await games.process_horse_bet(update, context, data)
        return

    # Admin Text Inputs (Add XP, Cut XP, Check User)
    if await admin.process_admin_text_input(update, context):
        return
        
    # Registration Flow
    if await manager.handle_registration_input(update, context):
        return

    # Private Chat Default
    if update.effective_chat.type == 'private':
        await update.message.reply_text("🤖 I use buttons only. Press /start")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = "🆘 **HELP MENU**\n\n/start - Open Menu\n/help - Show this\n\n**Admin Commands:**\n/addxp ID AMT\n/cutxp ID AMT\n/result MARKET NUM"
    await update.message.reply_text(txt, parse_mode='Markdown')

async def admin_shortcuts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shortcuts like /addxp 123 500"""
    cmd = update.message.text.split()[0]
    if cmd == '/result': await admin.resolve_market_command(update, context)
    # Add other shortcuts here if needed, but UI is preferred

if __name__ == '__main__':
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("🌐 WEB SERVER STARTED")

    app_bot = ApplicationBuilder().token(settings.BOT_TOKEN).build()
    
    app_bot.add_handler(CommandHandler('start', manager.start_command))
    app_bot.add_handler(CommandHandler('help', help_command))
    app_bot.add_handler(CommandHandler('result', admin.resolve_market_command))
    
    app_bot.add_handler(CallbackQueryHandler(handle_callback))
    app_bot.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_unknown_text))
    
    print("🚀 BOT IS LIVE")
    app_bot.run_polling()