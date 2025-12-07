from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import DATABASE_MEMORY as db
import SETTINGS_AUR_PRICES as settings
import DIALOGUES_AUR_RULES as dialogues

# --- SHOP ---
async def open_shop_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = db.get_user(query.from_user.id, "")
    inv = user.get('inventory', {})
    
    txt = f"""
🛒 **GAMING DUKAAN**
Jeb mein: {user['xp']} XP

🛡️ **Shield** (₹{settings.PRICES['shield']}): Haarne par XP bachega.
💡 **Hint** (₹{settings.PRICES['hint']}): Quiz mein madad.
⚡ **Double** (₹{settings.PRICES['double']}): Jeetne par 2x Maal.

🎒 **Tere Paas:**
🛡️ {inv.get('shield',0)} | 💡 {inv.get('hint',0)} | ⚡ {inv.get('double',0)}
"""

    kb = [
        [InlineKeyboardButton(f"🛡️ Buy Shield ({settings.PRICES['shield']})", callback_data='shop_buy|shield')],
        [InlineKeyboardButton(f"💡 Buy Hint ({settings.PRICES['hint']})", callback_data='shop_buy|hint')],
        [InlineKeyboardButton(f"⚡ Buy Double ({settings.PRICES['double']})", callback_data='shop_buy|double')],
        [InlineKeyboardButton("💎 BUY XP (UPI)", callback_data='show_upi')],
        [InlineKeyboardButton("🔙 Menu", callback_data='main_menu')]
    ]
    await query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def handle_shop_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    if query.data == 'show_upi':
        txt = f"💸 **XP KHARIDO**\n\nUPI ID:\n`{settings.ADMIN_UPI}`\n\n(Click to Copy)\nScreenshot Admin ko bhejo."
        await query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='menu_shop')]]), parse_mode='Markdown')
        return

    item = query.data.split('|')[1]
    uid = query.from_user.id
    user = db.get_user(uid, "")
    price = settings.PRICES.get(item, 9999)
    
    if user['xp'] >= price:
        new_inv = user.get('inventory', {})
        new_inv[item] = new_inv.get(item, 0) + 1
        db.update_user(uid, {"inventory": new_inv}, inc_dict={"xp": -price}, transaction=f"Bought {item}")
        await query.answer(dialogues.TEXTS['shop_success'])
        await open_shop_menu(update, context)
    else:
        await query.answer(dialogues.TEXTS['insufficient'], show_alert=True)

# --- BANK ---
async def open_bank_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    u = db.get_user(query.from_user.id, "")
    limit = int(u.get('total_deposit', 0) * 0.5)
    
    txt = f"🏦 **XP BANK**\n👛 Wallet: {u['xp']}\n🔐 Locker: {u['bank']}\n📉 Loan Limit: {limit}"
    
    kb = [
        [InlineKeyboardButton("📥 Jama 50%", callback_data='bank_act|dep_50'),
         InlineKeyboardButton("📥 Jama 100%", callback_data='bank_act|dep_100')],
        [InlineKeyboardButton("📤 Nikaal 50%", callback_data='bank_act|with_50'),
         InlineKeyboardButton("📤 Nikaal 100%", callback_data='bank_act|with_100')],
        [InlineKeyboardButton("💸 Loan Le Lo", callback_data='bank_act|loan')],
        [InlineKeyboardButton("🔙 Menu", callback_data='main_menu')]
    ]
    await query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def handle_bank_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    act = q.data.split('|')[1]
    uid = q.from_user.id
    u = db.get_user(uid, "")
    
    if 'dep' in act:
        percent = 0.5 if '50' in act else 1.0
        amount = int(u['xp'] * percent)
        if amount > 0:
            db.update_user(uid, None, inc_dict={'xp': -amount, 'bank': amount})
            await q.answer(f"✅ Jama: {amount} XP")
        else:
            await q.answer("❌ Jeb khali hai!", show_alert=True)
            
    elif 'with' in act:
        percent = 0.5 if '50' in act else 1.0
        amount = int(u['bank'] * percent)
        if amount > 0:
            db.update_user(uid, None, inc_dict={'xp': amount, 'bank': -amount})
            await q.answer(f"✅ Nikaala: {amount} XP")
        else:
            await q.answer("❌ Bank khali hai!", show_alert=True)
            
    elif act == 'loan':
        limit = int(u.get('total_deposit', 0) * 0.5)
        if u['loan_amount'] > 0:
            await q.answer("❌ Pehle purana loan chukao!", show_alert=True)
        elif u['xp'] > 10 or u['bank'] > 10:
            await q.answer("❌ Tumhare paas paisa hai. Loan nahi milega.", show_alert=True)
        elif limit < 50:
            await q.answer("❌ Trust issue. Aur deposit karo pehle.", show_alert=True)
        else:
            db.update_user(uid, {"loan_amount": limit}, inc_dict={'xp': limit}, transaction="Loan Taken")
            await q.answer(f"✅ Loan Approved: {limit} XP", show_alert=True)
            
    await open_bank_menu(update, context)