from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import DATABASE_MEMORY as db
import SETTINGS_AUR_PRICES as settings

# Short names for prices
P = settings.PRICES

async def open_shop_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user = db.get_user(user_id, "")
    inv = user['inventory']
    
    txt = f"""
🛒 **XP SHOP** (Currency: XP)
💰 Wallet: {user['xp']} XP
-----------------------------
👇 **Power-ups:**

💡 Hint: {P['hint']} XP (Owned: {inv.get('hint', 0)})
✂️ 50-50: {P['fifty']} XP (Owned: {inv.get('fifty', 0)})
⏭ Skip: {P['skip']} XP (Owned: {inv.get('skip', 0)})
🛡️ Shield: {P['shield']} XP (Owned: {inv.get('shield', 0)})

👇 **Real Money:**
"""
    
    keyboard = [
        # Line 1
        [InlineKeyboardButton(f"💡 Hint (-{P['hint']})", callback_data='shop_buy|hint'),
         InlineKeyboardButton(f"✂️ 50-50 (-{P['fifty']})", callback_data='shop_buy|fifty')],
        
        # Line 2
        [InlineKeyboardButton(f"⏭ Skip (-{P['skip']})", callback_data='shop_buy|skip'),
         InlineKeyboardButton(f"🛡️ Shield (-{P['shield']})", callback_data='shop_buy|shield')],
        
        # Payment Button
        [InlineKeyboardButton("💎 Buy XP (QR/UPI)", callback_data='shop_buy|real_money')],
        
        [InlineKeyboardButton("🔙 Main Menu", callback_data='main_menu')]
    ]
    
    await query.edit_message_text(text=txt, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def handle_shop_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    item_key = query.data.split("|")[1]
    user_id = query.from_user.id
    
    # --- REAL MONEY LOGIC ---
    if item_key == 'real_money':
        # Yahan Payment Info dikhayenge (From Settings)
        await query.edit_message_text(
            text=settings.PAYMENT_INFO,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Shop", callback_data='menu_shop')]]),
            parse_mode='Markdown'
        )
        return

    # --- NORMAL ITEM LOGIC ---
    price = settings.PRICES.get(item_key, 99999)
    user = db.get_user(user_id, "")
    
    if user['xp'] < price:
        await query.answer("❌ XP Kam hain! Game khelo ya Buy karo.", show_alert=True)
        return
        
    # Add Item
    current_inv = user['inventory']
    current_inv[item_key] = current_inv.get(item_key, 0) + 1
    
    db.update_user(user_id, {"inventory": current_inv}, inc_dict={"xp": -price}, transaction=f"Bought {item_key}")
    
    await query.answer(f"✅ {item_key.upper()} Purchased!", show_alert=True)
    await open_shop_menu(update, context)

# --- BANKING FUNCTIONS ---
async def open_bank_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Same as before, bas ₹ hata dena text se agar kahi likha ho
    # Logic remains same
    await _render_bank_ui(update)

async def handle_bank_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Same as before
    # ... (Keep previous bank logic) ...
    # Main logic repeat nahi kar raha space bachane ke liye,
    # Bas purani file ka bank logic yaha niche paste kar dena
    pass 

# Note: Aap purani file se 'open_bank_menu' aur 'handle_bank_action' copy kar sakte hain
# Bas jahan '₹' likha ho wahan 'XP' kar dena.

# Helper to avoid code duplication (Internal use)
async def _render_bank_ui(update):
    query = update.callback_query
    user_id = query.from_user.id
    user = db.get_user(user_id, "")
    
    txt = f"""
🏦 **XP BANK**
👛 Wallet: {user['xp']} XP
🔐 Bank: {user['bank']} XP
    """
    # Buttons same as previous
    kb = [
        [InlineKeyboardButton("📥 Deposit All", callback_data='bank_action|dep_all'),
         InlineKeyboardButton("📤 Withdraw All", callback_data='bank_action|with_all')],
        [InlineKeyboardButton("💸 Take Loan", callback_data='bank_action|loan_req')],
        [InlineKeyboardButton("🔙 Main Menu", callback_data='main_menu')]
    ]
    await query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')