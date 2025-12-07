from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import ContextTypes
import DATABASE_MEMORY as db
import SETTINGS_AUR_PRICES as settings

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. GROUP CHAT CHECK
    if update.effective_chat.type != constants.ChatType.PRIVATE:
        me = await context.bot.get_me()
        kb = [[InlineKeyboardButton("🚀 START IN DM", url=f"https://t.me/{me.username}?start=1")]]
        await update.message.reply_text("👋 **Hi!**\n\nMain Group mein baat nahi karta.\nGame khelne ke liye DM mein aao!", reply_markup=InlineKeyboardMarkup(kb))
        return

    user = update.effective_user
    user_data = db.get_user(user.id, user.first_name)
    
    if user_data.get('is_banned'):
        await update.message.reply_text("🚫 **YOU ARE BANNED**")
        return

    if not user_data.get('is_registered'):
        await start_registration_flow(update, context)
    else:
        await show_main_menu(update, context, user_data)

async def start_registration_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db.update_user(user_id, {"reg_step": "waiting_gender"})
    kb = [[InlineKeyboardButton("👨 Male", callback_data="reg_gender|Male"),
           InlineKeyboardButton("👩 Female", callback_data="reg_gender|Female")]]
    await update.message.reply_text("👋 **Welcome!** Register to play.\nSelect Gender:", reply_markup=InlineKeyboardMarkup(kb))

async def handle_gender_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    gender = q.data.split("|")[1]
    db.update_user(q.from_user.id, {"gender": gender, "reg_step": "waiting_name"})
    await q.edit_message_text(f"✅ Gender: {gender}\n\n✍️ **Naam batao:** Apne Aadhaar wala Real Name likho:")

async def handle_registration_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Group message ignore in registration
    if update.effective_chat.type != constants.ChatType.PRIVATE: return False

    text = update.message.text
    user_data = db.get_user(user.id, "")
    
    if not user_data or user_data.get('is_registered'): return False
    step = user_data.get('reg_step')
    
    if step == "waiting_name":
        db.update_user(user.id, {"real_name": text, "reg_step": "waiting_city"})
        await update.message.reply_text(f"✅ Hello {text}!\n\n🏙️ **Shahar (City) ka naam likho:**")
        return True

    elif step == "waiting_city":
        db.update_user(user.id, {"city": text, "reg_step": "waiting_mobile"})
        await update.message.reply_text("✅ Saved.\n\n📱 **Mobile Number likho:**")
        return True

    elif step == "waiting_mobile":
        db.update_user(user.id, {
            "mobile": text, 
            "reg_step": "completed", 
            "is_registered": True, 
            "xp": 150 # Signup Bonus
        })
        
        # Admin Alert
        alert = f"🚨 **NEW PLAYER JOINED**\nName: {user_data.get('real_name')}\nCity: {user_data.get('city')}\nMobile: {text}\nID: `{user.id}`"
        for aid in settings.ADMIN_IDS:
            try: await context.bot.send_message(aid, alert, parse_mode='Markdown')
            except: pass
            
        await update.message.reply_text("🎉 **Registration Complete!**\n🎁 **150 XP Bonus Added!**")
        await show_main_menu(update, context, db.get_user(user.id, ""))
        return True

    return False

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_data):
    # Admin Mode Toggle check
    is_admin_mode = context.user_data.get('admin_view', False)
    
    txt = f"🎮 **MYSTERY PRO**\nID: `{user_data['_id']}`\n💎 XP: {user_data['xp']}"
    
    kb = [
        [InlineKeyboardButton("🎮 PLAY GAMES", callback_data='menu_games')],
        [InlineKeyboardButton("🛍️ SHOP & BUY XP", callback_data='menu_shop')],
        [InlineKeyboardButton("🏦 BANK & LOAN", callback_data='menu_bank')],
        [InlineKeyboardButton("🎒 PROFILE", callback_data='show_profile')]
    ]
    
    # Show Admin Button ONLY if user is Admin
    if user_data['_id'] in settings.ADMIN_IDS:
        kb.insert(0, [InlineKeyboardButton("⚙️ ADMIN PANEL", callback_data='admin_dashboard')])
        
    reply_markup = InlineKeyboardMarkup(kb)
    
    if update.message: await update.message.reply_text(txt, reply_markup=reply_markup, parse_mode='Markdown')
    else: await update.callback_query.edit_message_text(txt, reply_markup=reply_markup, parse_mode='Markdown')

async def show_profile(update, context):
    q = update.callback_query
    u = db.get_user(q.from_user.id, "")
    
    admin_tag = ""
    if u['_id'] in settings.ADMIN_IDS:
        admin_tag = f"\n👑 **ADMIN ACCESS GRANTED**\n🔑 Unique ID: `{u['_id']}`"

    txt = f"👤 **PROFILE**\nName: {u.get('real_name')}\nCity: {u.get('city')}\nMobile: {u.get('mobile')}\n{admin_tag}\n\n🏆 Wins: {u['stats']['wins']}\n📉 Loans Taken: {u['loan_amount'] > 0}"
    await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='main_menu')]]), parse_mode='Markdown')