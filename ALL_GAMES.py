from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
import SETTINGS_AUR_PRICES as settings
import DATABASE_MEMORY as db
import datetime
import pytz

def is_market_open(open_h, open_m, close_h, close_m):
    """Checks if current time is within open/close range, handling midnight"""
    now = datetime.datetime.now(settings.TIMEZONE)
    current_time = now.hour * 60 + now.minute
    start_time = open_h * 60 + open_m
    end_time = close_h * 60 + close_m

    if start_time < end_time:
        # Standard day (e.g., 9 AM to 5 PM)
        return start_time <= current_time < end_time
    else:
        # Crosses midnight (e.g., 10 PM to 2 AM)
        return current_time >= start_time or current_time < end_time

async def game_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    base = settings.WEB_APP_URL
    
    keyboard = [
        [InlineKeyboardButton("🐍 Neon Snake", web_app=WebAppInfo(url=f"{base}/game/snake"))],
        [InlineKeyboardButton("🎰 Neon Slots", web_app=WebAppInfo(url=f"{base}/game/slots"))],
        [InlineKeyboardButton("🎲 Neon Dice", web_app=WebAppInfo(url=f"{base}/game/dice"))],
        [InlineKeyboardButton("🧠 Neon Quiz", web_app=WebAppInfo(url=f"{base}/game/quiz"))],
        [InlineKeyboardButton("🎱 LUCKY BOWL (Jackpot)", callback_data='menu_bowl')],
        [InlineKeyboardButton("🐎 LUCK WITH HORSE (Satta)", callback_data='menu_horse')],
        [InlineKeyboardButton("🔙 Main Menu", callback_data='main_menu')]
    ]
    await query.edit_message_text("🎮 **GAME ZONE**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def menu_bowl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    base = settings.WEB_APP_URL
    kb = [[InlineKeyboardButton("🎱 PLAY NOW", web_app=WebAppInfo(url=f"{base}/premium/bowl"))],
          [InlineKeyboardButton("🔙 Back", callback_data='menu_games')]]
    await query.edit_message_text("🎱 **LUCKY BOWL**\nJackpot: 90x\nCost: 100 XP", reply_markup=InlineKeyboardMarkup(kb))

async def menu_horse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    base = settings.WEB_APP_URL
    
    status_lines = []
    for m_name, t in settings.MARKETS.items():
        is_open = is_market_open(t['open_h'], t['open_m'], t['close_h'], t['close_m'])
        icon = "🟢" if is_open else "🔴"
        status_lines.append(f"{icon} {m_name}")
        
    txt = f"🐎 **HORSE BETTING (90x)**\nMin Bet: 50 XP\n\n**MARKET STATUS:**\n" + "\n".join(status_lines)
    kb = [[InlineKeyboardButton("🐎 OPEN BETTING GRID", web_app=WebAppInfo(url=f"{base}/premium/horse"))],
          [InlineKeyboardButton("🔙 Back", callback_data='menu_games')]]
    await query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def process_horse_bet(update: Update, context: ContextTypes.DEFAULT_TYPE, data_str):
    # data: "bet_horse|market|number|amount"
    try:
        _, market, num, amt = data_str.split("|")
        num = int(num)
        amt = int(amt)
        user_id = update.effective_user.id
        
        # 1. Market Validation
        m_data = settings.MARKETS.get(market)
        if not m_data or not is_market_open(m_data['open_h'], m_data['open_m'], m_data['close_h'], m_data['close_m']):
            await update.message.reply_text(f"🔴 **{market} Market Closed!** Betting Rejected.")
            return

        # 2. Balance Check
        user = db.get_user(user_id, "")
        if user['xp'] < amt:
            await update.message.reply_text("❌ Insufficient XP!")
            return

        # 3. Process Bet
        db.update_user(user_id, None, inc_dict={"xp": -amt}, transaction=f"Bet {market} #{num}")
        db.save_bet(user_id, "Horse", market, num, amt)
        
        await update.message.reply_text(f"✅ **BET PLACED!**\nMarket: {market}\nNumber: {num}\nAmount: {amt} XP")
        
    except Exception as e:
        print(f"Bet Error: {e}")