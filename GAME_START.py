import threading
import sys
import logging
import json
import requests
import os
import time
import random  # <--- YE MISSING THA, AB ADD KAR DIYA HAI
from flask import Flask, render_template, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
    MessageHandler, ContextTypes, filters
)

# --- MODULES ---
import SETTINGS_AUR_PRICES as settings
import DATABASE_MEMORY as db
import MANAGER_HANDLE as manager
import ALL_GAMES as games
import ADMIN_POWER as admin
import BANK_AUR_SHOP as bank
import DIALOGUES_AUR_RULES as dialogues

# --- FLASK APP ---
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home(): return "🤖 MYSTERY HUNT IS ACTIVE"

# --- GAME ROUTES (Frontend serve karna) ---
@app.route('/game/<name>')
def serve_game(name):
    valid_games = ['snake', 'slots', 'dice', 'quiz']
    if name in valid_games: return render_template(f'{name}.html')
    return "Game Not Found", 404

@app.route('/premium/<name>')
def serve_premium(name):
    valid_games = ['bowl', 'horse']
    if name in valid_games: return render_template(f'{name}.html')
    return "Premium Game Not Found", 404

# --- API ENDPOINTS (Strict Logic) ---
@app.route('/api/deduct_fee', methods=['POST'])
def api_deduct():
    try:
        data = request.json
        user_id = int(data.get('user_id'))
        amount = int(data.get('amount', 0))
        game = data.get('game_name')

        user = db.get_user(user_id, "")
        if not user: return jsonify({"status": "fail", "msg": "User unknown"})

        # Check Shield Logic (Only for losses, but here we deduct entry fee)
        # Entry Fee is mandatory.
        if user['xp'] >= amount:
            db.update_user(user_id, None, inc_dict={"xp": -amount, "stats.games_played": 1}, transaction=f"Played {game}")
            return jsonify({"status": "success", "new_balance": user['xp'] - amount})
        else:
            return jsonify({"status": "fail", "msg": "Insufficient Funds"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})

@app.route('/api/claim_win', methods=['POST'])
def api_claim():
    try:
        data = request.json
        user_id = int(data.get('user_id'))
        amount = int(data.get('amount'))
        game_name = data.get('game_name')

        user = db.get_user(user_id, "")
        
        # Double Tap Logic
        inv = user.get('inventory', {})
        if inv.get('double', 0) > 0:
            amount = amount * 2
            # Decrease inventory
            inv['double'] -= 1
            db.update_user(user_id, {"inventory": inv}, transaction="Used Double Tap")

        # Loan Auto-Deduct
        loan = user.get('loan_amount', 0)
        final_payout = amount
        deducted = 0
        
        if loan > 0:
            if amount >= loan:
                deducted = loan
                final_payout = amount - loan
                db.update_user(user_id, {"loan_amount": 0}, inc_dict={"xp": -loan}, transaction="Loan Paid Auto")
            else:
                deducted = amount
                final_payout = 0
                db.update_user(user_id, None, inc_dict={"loan_amount": -deducted, "xp": -deducted})

        db.update_user(user_id, None, inc_dict={"xp": amount, "stats.wins": 1}, transaction=f"Won {game_name}")
        
        # FIX: Ab 'random' defined hai upar import mein
        msg = f"{random.choice(dialogues.TEXTS['win_hype'])}\n💰 **Won:** {amount} XP"
        if deducted > 0: msg += f"\n📉 **Loan Cut:** {deducted} XP"
        
        # Async Alert
        send_alert(user_id, msg)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})

def send_alert(chat_id, text):
    try:
        requests.post(f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
    except: pass

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# --- TELEGRAM HANDLERS ---
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    # Routing
    if data == 'main_menu': await manager.show_main_menu(update, context, db.get_user(query.from_user.id, ""))
    elif data == 'show_profile': await manager.show_profile(update, context)
    
    elif data == 'menu_games': await games.game_menu(update, context)
    elif data == 'menu_bowl': await games.menu_bowl(update, context)
    elif data == 'menu_horse': await games.menu_horse(update, context)
    elif data.startswith('rules|'): await games.show_rules(update, context)
    
    elif data == 'menu_shop': await bank.open_shop_menu(update, context)
    elif data.startswith('shop_buy|') or data == 'show_upi': await bank.handle_shop_buy(update, context)
    
    elif data == 'menu_bank': await bank.open_bank_menu(update, context)
    elif data.startswith('bank_act|'): await bank.handle_bank_action(update, context)
    
    elif data == 'admin_dashboard': await admin.open_admin_panel(update, context)
    elif data == 'admin_player_view': await manager.show_main_menu(update, context, db.get_user(query.from_user.id, ""))
    elif data.startswith('admin_'): await admin.handle_admin_buttons(update, context)
    
    elif data.startswith('reg_gender|'): await manager.handle_gender_selection(update, context)
    else: await query.answer("⚠️ Unknown Button")

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # WebApp Data (Horse Game Bets)
    if update.effective_message.web_app_data:
        data = update.effective_message.web_app_data.data
        if data.startswith("bet_horse"):
            await games.process_horse_bet(update, context, data)
        return

    # Admin Inputs
    if await admin.process_admin_text_input(update, context): return
    
    # Registration Inputs
    if await manager.handle_registration_input(update, context): return

async def group_join_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id: continue
        kb = [[InlineKeyboardButton("🚀 Go to DM (Start Game)", url=f"https://t.me/{context.bot.username}?start=1")]]
        await update.message.reply_text(
            dialogues.TEXTS['group_welcome'].format(name=member.first_name),
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode='Markdown'
        )

if __name__ == '__main__':
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    app_bot = ApplicationBuilder().token(settings.BOT_TOKEN).build()
    
    app_bot.add_handler(CommandHandler('start', manager.start_command))
    app_bot.add_handler(CallbackQueryHandler(handle_callback))
    app_bot.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, group_join_alert))
    app_bot.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_msg))
    
    print("🚀 BOT IS LIVE")
    app_bot.run_polling()