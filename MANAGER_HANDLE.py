from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import datetime
import pytz 

# Hamari files
import DIALOGUES_AUR_RULES as dialogues
import DATABASE_MEMORY as db
import SETTINGS_AUR_PRICES as settings
import ADMIN_POWER as admin 

# --- TIME CHECKER ---
def is_shop_open():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(ist)
    return 10 <= now.hour < 21

# --- START COMMAND ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_type = update.effective_chat.type
    user_id = user.id
    
    # Database Get/Create
    user_data = db.get_user(user_id, user.first_name)
    
    # 1. GROUP LOGIC
    if chat_type != 'private':
        welcome_txt = dialogues.TEXTS['group_welcome'].format(
            name=user.first_name, bonus="20 XP", rank=dialogues.get_rank_name(user_data['lifetime_xp']))
        kb = [[InlineKeyboardButton("🚀 Go to Personal DM", url=f"https://t.me/{context.bot.username}?start=group_entry")]]
        await update.message.reply_text(text=welcome_txt, reply_markup=InlineKeyboardMarkup(kb))
        return

    # 2. PERSONAL DM LOGIC
    
    # --- A. REGISTRATION CHECK (NEW LOGIC) ---
    # Agar banda registered nahi hai, to pehle registration karwao
    if not user_data.get('is_registered'):
        await start_registration_flow(update, context)
        return

    # --- B. TIME CHECK (Admin Bypass) ---
    if not is_shop_open() and user_id not in settings.ADMIN_IDS:
        ist = pytz.timezone('Asia/Kolkata')
        time_now = datetime.datetime.now(ist).strftime("%I:%M %p")
        closed_txt = dialogues.TEXTS['shop_closed'].format(current_time=time_now)
        buttons = [[InlineKeyboardButton("🎒 Check Profile", callback_data='show_profile')]]
        await update.message.reply_text(closed_txt, reply_markup=InlineKeyboardMarkup(buttons))
        return

    # 3. SHOW MAIN MENU (Agar sab sahi hai)
    await show_main_menu(update, context, user_data)

# ==============================================================================
#  REGISTRATION SYSTEM (Step-by-Step Form)
# ==============================================================================

async def start_registration_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 1: Gender Pucho"""
    user_id = update.effective_user.id
    
    # DB me mark karo ki user gender step par hai
    db.update_user(user_id, {"reg_step": "waiting_gender"})
    
    txt = """
👋 **SWAGAT HAI GAMER!**
Game shuru karne se pehle humein aapki thodi details chahiye.
_(Taki jeetne par hum aapko Prize Money bhej sakein)_

Sabse pehle, aapka **Gender** kya hai? 👇
    """
    kb = [
        [InlineKeyboardButton("👨 Male", callback_data="reg_gender|Male"),
         InlineKeyboardButton("👩 Female", callback_data="reg_gender|Female")]
    ]
    
    # Msg bhejo
    if update.callback_query:
        await update.callback_query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
    else:
        await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def handle_gender_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Button dabane par Gender save karega"""
    query = update.callback_query
    gender_val = query.data.split("|")[1] # 'Male' or 'Female'
    user_id = query.from_user.id
    
    # Save Gender -> Move to Name Step
    db.update_user(user_id, {"gender": gender_val, "reg_step": "waiting_name"})
    
    await query.edit_message_text(f"✅ Gender: **{gender_val}**\n\n✍️ Ab apna **Pura Naam (Real Name)** type karke bhejo:")

async def handle_registration_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Jab user kuch TYPE karega, ye function check karega ki wo Registration ka jawab hai ya nahi.
    Returns: True (Agar registration chal raha tha), False (Agar normal chat thi)
    """
    user = update.effective_user
    text = update.message.text
    user_data = db.get_user(user.id, user.first_name)
    
    # Agar Registered hai to yahan kuch mat karo
    if user_data.get('is_registered'):
        return False 
    
    step = user_data.get('reg_step')
    
    # STEP 2: NAME
    if step == "waiting_name":
        db.update_user(user.id, {"real_name": text, "reg_step": "waiting_city"})
        await update.message.reply_text(f"✅ Naam Save hua: **{text}**\n\n🏙️ Ab apni **City (Shahar)** ka naam likho:")
        return True

    # STEP 3: CITY
    elif step == "waiting_city":
        db.update_user(user.id, {"city": text, "reg_step": "waiting_mobile"})
        await update.message.reply_text(f"✅ City: **{text}**\n\n📱 **Last Step:** Apna **Paytm/UPI Mobile Number** likho (Winning ke liye):")
        return True

    # STEP 4: MOBILE (Final)
    elif step == "waiting_mobile":
        # Validation (Sirf numbers hone chahiye)
        if not text.isdigit() or len(text) < 10:
            await update.message.reply_text("❌ Galat Number! Kripya sahi 10 digit ka mobile number likhein.")
            return True
            
        # Complete Registration
        db.update_user(user.id, {
            "mobile": text, 
            "reg_step": "completed", 
            "is_registered": True
        })
        
        await update.message.reply_text("🎉 **Registration Successful!**\nAb aap Game khel sakte hain.")
        
        # Menu dikhao
        await show_main_menu(update, context, db.get_user(user.id, ""))
        return True
        
    return False

# ==============================================================================
#  MAIN MENUS & PROFILE
# ==============================================================================

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_data):
    user_id = user_data['_id']
    rank_name = dialogues.get_rank_name(user_data['lifetime_xp'])
    role_title = "👑 BOSS (Admin)" if user_id in settings.ADMIN_IDS else "Player"
    
    welcome_text = f"""
👋 **Hello {user_data['real_name']}!**
🆔 **Unique ID:** `{user_id}`
🎭 **Role:** {role_title}
🏅 **Rank:** {rank_name}
💎 **Wallet:** {user_data['xp']} XP

Kya karna hai? 👇
    """

    keyboard = [
        [InlineKeyboardButton("🎮 Play Games", callback_data='menu_games'), 
         InlineKeyboardButton("🛍️ Shop & Lifelines", callback_data='menu_shop')],
        
        [InlineKeyboardButton("🏦 XP Bank", callback_data='menu_bank'), 
         InlineKeyboardButton("🎒 My Profile", callback_data='show_profile')],
        
        [InlineKeyboardButton("📜 Help & Rules", callback_data='show_rules')]
    ]
    
    # Admin Button
    if user_id in settings.ADMIN_IDS:
        keyboard.insert(0, [InlineKeyboardButton("⚙️ OPEN ADMIN DASHBOARD", callback_data='admin_dashboard')])

    if update.message:
        await update.message.reply_text(text=welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        await update.callback_query.edit_message_text(text=welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = db.get_user(user_id, "")
    rank = dialogues.get_rank_name(data['lifetime_xp'])
    
    # Profile me ab Personal Data bhi dikhega
    profile_txt = f"""
👤 **PLAYER PROFILE**
--------------------
📛 **Name:** {data.get('real_name', 'Unknown')}
🏙️ **City:** {data.get('city', 'Unknown')}
📱 **Mobile:** {data.get('mobile', 'Unknown')}
🚻 **Gender:** {data.get('gender', 'Unknown')}
--------------------
🆔 **ID:** `{user_id}` (Tap to Copy)
🏅 **Rank:** {rank}
💰 **Wallet:** {data['xp']} XP
🏦 **Bank:** {data['bank']} XP
📊 **Games Played:** {data['stats']['games_played']}
    """
    keyboard = [[InlineKeyboardButton("🔙 Main Menu", callback_data='main_menu')]]
    await query.edit_message_text(text=profile_txt, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')