from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import SETTINGS_AUR_PRICES as settings
import DATABASE_MEMORY as db
import asyncio

# Global Variable
IS_MAINTENANCE_MODE = False

def is_admin(user_id):
    """Check karta hai ki user Admin list me hai ya nahi"""
    # Agar list hai to check karega, agar single int hai to compare karega
    if isinstance(settings.ADMIN_IDS, list):
        return user_id in settings.ADMIN_IDS
    return user_id == settings.ADMIN_IDS

# --- 1. ADMIN DASHBOARD MENU (Buttons) ---
async def open_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    if not is_admin(user_id):
        await query.answer("❌ Sirf Admin ke liye!", show_alert=True)
        return

    txt = """
⚙️ **ADMIN GOD MODE** ⚙️
Control everything from here without typing commands.
    """
    
    keyboard = [
        [InlineKeyboardButton("💰 Give 500 XP (Self)", callback_data='admin_act|give_self'),
         InlineKeyboardButton("💰 Give 5000 XP (Self)", callback_data='admin_act|give_self_big')],
        
        [InlineKeyboardButton("🛑 Maintenance ON", callback_data='admin_act|maint_on'),
         InlineKeyboardButton("🟢 Maintenance OFF", callback_data='admin_act|maint_off')],
        
        [InlineKeyboardButton("🔄 Reset My Data", callback_data='admin_act|reset_self')],
        
        [InlineKeyboardButton("🔙 Normal Menu", callback_data='main_menu')]
    ]
    
    await query.edit_message_text(text=txt, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# --- 2. ACTION HANDLER (Button Logic) ---
async def handle_admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # FIX: Global declaration sabse upar honi chahiye
    global IS_MAINTENANCE_MODE 
    
    query = update.callback_query
    data = query.data.split('|')[1]
    user_id = query.from_user.id
    
    if not is_admin(user_id): return

    msg = ""
    
    if data == 'give_self':
        db.update_user(user_id, None, inc_dict={'xp': 500})
        msg = "✅ Added 500 XP to your wallet."
        
    elif data == 'give_self_big':
        db.update_user(user_id, None, inc_dict={'xp': 5000})
        msg = "✅ Added 5000 XP (Richie Rich!)."
        
    elif data == 'maint_on':
        IS_MAINTENANCE_MODE = True
        msg = "🔴 Maintenance Mode ENABLED."
        
    elif data == 'maint_off':
        IS_MAINTENANCE_MODE = False
        msg = "🟢 Maintenance Mode DISABLED."
        
    elif data == 'reset_self':
        # Reset Logic
        empty_stats = {
            "xp": 0, "bank": 0, "lifetime_xp": 0, "loan_amount": 0,
            "inventory": {"shield": 0, "double_xp": 0, "hint": 0},
            "stats": {"wins": 0, "loss": 0, "games_played": 0}
        }
        db.update_user(user_id, empty_stats) # Set entire dict
        msg = "♻️ Your Data has been RESET to 0."

    await query.answer(msg, show_alert=True)
    # Optional: Panel refresh nahi kar rahe taaki spam na lage

# --- 3. MANUAL COMMANDS (Slash Commands) ---

async def broadcast_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Command: /broadcast Hello """
    user_id = update.effective_user.id
    if not is_admin(user_id): return

    msg = " ".join(context.args)
    if not msg:
        await update.message.reply_text("❌ Msg likho: `/broadcast Hello`", parse_mode='Markdown')
        return

    await update.message.reply_text("📢 Sending Broadcast...")
    
    # Database se IDs nikalo
    all_users = db.users_collection.find({}, {"_id": 1})
    count = 0
    for user in all_users:
        try:
            await context.bot.send_message(chat_id=user['_id'], text=f"📢 **ANNOUNCEMENT**\n\n{msg}", parse_mode='Markdown')
            count += 1
            await asyncio.sleep(0.1)
        except:
            pass
            
    await update.message.reply_text(f"✅ Sent to {count} users.")

async def give_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Command: /give 12345 500 """
    if not is_admin(update.effective_user.id): return
    try:
        tid = int(context.args[0])
        amt = int(context.args[1])
        db.update_user(tid, None, inc_dict={"xp": amt})
        await update.message.reply_text(f"✅ Sent {amt} XP to {tid}")
    except:
        await update.message.reply_text("❌ Error. Usage: `/give ID Amount`")

async def check_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Command: /check 12345 """
    if not is_admin(update.effective_user.id): return
    try:
        tid = int(context.args[0])
        data = db.get_user(tid, "User")
        await update.message.reply_text(f"📄 Report:\nXP: {data.get('xp')}\nBank: {data.get('bank')}")
    except:
        await update.message.reply_text("❌ Usage: `/check ID`")

async def reset_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Command: /reset 12345 """
    if not is_admin(update.effective_user.id): return
    try:
        tid = int(context.args[0])
        db.users_collection.delete_one({"_id": tid})
        if tid in db.user_cache: del db.user_cache[tid]
        await update.message.reply_text(f"♻️ User {tid} RESET complete.")
    except:
        await update.message.reply_text("❌ Usage: `/reset ID`")

async def maintenance_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # FIX: Global declaration sabse upar
    global IS_MAINTENANCE_MODE
    
    if not is_admin(update.effective_user.id): return
    try:
        arg = context.args[0].lower()
        if arg == 'on': IS_MAINTENANCE_MODE = True
        elif arg == 'off': IS_MAINTENANCE_MODE = False
        await update.message.reply_text(f"🔧 Maintenance: {IS_MAINTENANCE_MODE}")
    except:
        await update.message.reply_text("❌ Usage: `/maintenance on/off`")