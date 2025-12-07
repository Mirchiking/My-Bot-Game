from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import ContextTypes
import DATABASE_MEMORY as db
import SETTINGS_AUR_PRICES as settings
import DIALOGUES_AUR_RULES as dialogues

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Direct DM Logic
    if update.effective_chat.type == constants.ChatType.PRIVATE:
        user_data = db.get_user(user.id, user.first_name)
        
        if user_data.get('is_banned'):
            await update.message.reply_text("🚫 **BANNED!** Admin ne laat maar ke nikaal diya hai.")
            return

        if not user_data.get('is_registered'):
            await start_registration_flow(update, context)
        else:
            await show_main_menu(update, context, user_data)
    else:
        # Group logic handled in GAME_START via StatusUpdate
        pass

async def start_registration_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.update_user(update.effective_user.id, {"reg_step": "waiting_gender"})
    kb = [[InlineKeyboardButton("👨 Ladka", callback_data="reg_gender|Male"),
           InlineKeyboardButton("👩 Ladki", callback_data="reg_gender|Female")]]
    await update.message.reply_text("👋 **Namaste!** Pehle ye batao tum ho kaun?", reply_markup=InlineKeyboardMarkup(kb))

async def handle_gender_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    db.update_user(q.from_user.id, {"gender": q.data.split("|")[1], "reg_step": "waiting_name"})
    await q.edit_message_text("✅ Gender Set.\n\n✍️ **Ab apna Asli Naam likho:**")

async def handle_registration_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if update.effective_chat.type != constants.ChatType.PRIVATE: return False
    
    text = update.message.text
    u_data = db.get_user(user.id, "")
    step = u_data.get('reg_step')

    if step == "waiting_name":
        db.update_user(user.id, {"real_name": text, "reg_step": "waiting_city"})
        await update.message.reply_text(f"Swagat hai **{text}**!\n\n🏙️ **Kaunse Shehar (City) se ho?**")
        return True
        
    if step == "waiting_city":
        db.update_user(user.id, {"city": text, "reg_step": "waiting_mobile"})
        await update.message.reply_text("Theek hai.\n\n📱 **Mobile Number kya hai?** (Fake mat dena):")
        return True
        
    if step == "waiting_mobile":
        db.update_user(user.id, {"mobile": text, "reg_step": "completed", "is_registered": True, "xp": 100})
        await update.message.reply_text("🎉 **Registration Done!**\n🎁 **100 XP Free Mile Hain!**")
        await show_main_menu(update, context, db.get_user(user.id, ""))
        return True
        
    return False

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_data):
    txt = dialogues.TEXTS['welcome_dm'].format(
        greeting=dialogues.get_random_greeting(),
        name=user_data['real_name'],
        user_id=user_data['_id'],
        rank=dialogues.get_rank_name(user_data['xp']),
        xp=user_data['xp'],
        bank=user_data['bank']
    )
    
    kb = [
        [InlineKeyboardButton("🎮 GAME ZONE", callback_data='menu_games')],
        [InlineKeyboardButton("🛍️ DUKAAN (Shop)", callback_data='menu_shop'),
         InlineKeyboardButton("🏦 BANK", callback_data='menu_bank')],
        [InlineKeyboardButton("🎒 PROFILE", callback_data='show_profile'),
         InlineKeyboardButton("🆘 HELP & RULES", callback_data='rules|general')]
    ]
    
    # Admin Separate Button
    if user_data['_id'] in settings.ADMIN_IDS:
        kb.insert(0, [InlineKeyboardButton("⚙️ ADMIN DASHBOARD", callback_data='admin_dashboard')])
        
    reply_markup = InlineKeyboardMarkup(kb)
    
    if update.message: await update.message.reply_text(txt, reply_markup=reply_markup, parse_mode='Markdown')
    else: await update.callback_query.edit_message_text(txt, reply_markup=reply_markup, parse_mode='Markdown')

async def show_profile(update, context):
    q = update.callback_query
    u = db.get_user(q.from_user.id, "")
    inv = u.get('inventory', {})
    
    txt = f"""
👤 **PLAYER PROFILE**
━━━━━━━━━━━━━━━━
📛 Name: {u.get('real_name')}
📍 City: {u.get('city')}
📱 Mobile: {u.get('mobile')}
🏆 Wins: {u['stats']['wins']}

🎒 **INVENTORY:**
🛡️ Shield: {inv.get('shield',0)}
💡 Hint: {inv.get('hint',0)}
⚡ Double: {inv.get('double',0)}
"""
    await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='main_menu')]]), parse_mode='Markdown')