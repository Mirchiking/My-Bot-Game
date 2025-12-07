from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
import SETTINGS_AUR_PRICES as settings
import DATABASE_MEMORY as db
import datetime

async def game_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    base = settings.WEB_APP_URL
    
    kb = [
        [InlineKeyboardButton("🐍 SNAKE", web_app=WebAppInfo(url=f"{base}/game/snake")),
         InlineKeyboardButton("🎰 SLOTS", web_app=WebAppInfo(url=f"{base}/game/slots"))],
        [InlineKeyboardButton("🎲 DICE", web_app=WebAppInfo(url=f"{base}/game/dice")),
         InlineKeyboardButton("🧠 QUIZ", web_app=WebAppInfo(url=f"{base}/game/quiz"))],
        [InlineKeyboardButton("🎱 LUCKY BOWL", callback_data='menu_bowl')],
        [InlineKeyboardButton("🐎 HORSE RACE", callback_data='menu_horse')],
        [InlineKeyboardButton("🔙 Main Menu", callback_data='main_menu')]
    ]
    await query.edit_message_text("🎮 **GAME ARENA**\nKismat aajmao!", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def menu_bowl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    base = settings.WEB_APP_URL
    kb = [[InlineKeyboardButton("🎱 PLAY NOW (90x)", web_app=WebAppInfo(url=f"{base}/premium/bowl"))],
          [InlineKeyboardButton("🔙 Back", callback_data='menu_games')]]
    await query.edit_message_text("🎱 **LUCKY BOWL**\nJackpot: 90x\nEntry: 100 XP", reply_markup=InlineKeyboardMarkup(kb))

async def menu_horse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    base = settings.WEB_APP_URL
    
    # Check Market Status
    status_msg = "🐎 **HORSE MARKETS**\n\n"
    for name, t in settings.MARKETS.items():
        now = datetime.datetime.now(settings.TIMEZONE)
        curr = now.hour * 60 + now.minute
        start = t['open_h'] * 60 + t['open_m']
        end = t['close_h'] * 60 + t['close_m']
        
        is_open = False
        if start < end: is_open = start <= curr < end
        else: is_open = curr >= start or curr < end
        
        icon = "🟢 OPEN" if is_open else "🔴 CLOSED"
        status_msg += f"• {name}: {icon}\n"

    kb = [[InlineKeyboardButton("🐎 PLACE BETS", web_app=WebAppInfo(url=f"{base}/premium/horse"))],
          [InlineKeyboardButton("🔙 Back", callback_data='menu_games')]]
    await query.edit_message_text(status_msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def show_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Specific Rule Display Logic (Not critical, generic text used in DIALOGUES)
    await update.callback_query.answer("Rules padh lo upar!", show_alert=True)

async def process_horse_bet(update: Update, context: ContextTypes.DEFAULT_TYPE, data_str):
    # Format: bet_horse|MARKET|NUM|AMT
    try:
        parts = data_str.split('|')
        market = parts[1]
        num = int(parts[2])
        amt = int(parts[3])
        user_id = update.effective_user.id
        
        user = db.get_user(user_id, "")
        if user['xp'] < amt:
            await update.message.reply_text(f"❌ **Bet Failed:** XP kam hain ({user['xp']})")
            return

        db.update_user(user_id, None, inc_dict={"xp": -amt}, transaction=f"Bet Horse {market}")
        db.save_bet(user_id, "Horse", market, num, amt)
        await update.message.reply_text(f"✅ **BET PLACED!**\n🐎 {market} | #{num}\n💰 {amt} XP")
    except Exception as e:
        print(f"Bet Error: {e}")