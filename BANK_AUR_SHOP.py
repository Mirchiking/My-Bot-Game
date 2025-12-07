from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import DATABASE_MEMORY as db
import SETTINGS_AUR_PRICES as settings

# --- SHOP ---
async def open_shop_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = db.get_user(query.from_user.id, "")
    inv = user.get('inventory', {})
    
    txt = f"🛍️ **SHOP** | XP: {user['xp']}\n\n"
    txt += f"🛡️ Shield: {inv.get('shield',0)} | 💡 Hint: {inv.get('hint',0)}\n"
    txt += f"✂️ 50-50: {inv.get('fifty',0)} | ⏭ Skip: {inv.get('skip',0)}\n"
    txt += f"⚡ Double: {inv.get('double',0)}\n"

    kb = [
        [InlineKeyboardButton("🛡️ Shield (50)", callback_data='shop_buy|shield'),
         InlineKeyboardButton("💡 Hint (50)", callback_data='shop_buy|hint')],
        [InlineKeyboardButton("✂️ 50-50 (50)", callback_data='shop_buy|fifty'),
         InlineKeyboardButton("⏭ Skip (50)", callback_data='shop_buy|skip')],
        [InlineKeyboardButton("⚡ Double Tap (75)", callback_data='shop_buy|double')],
        [InlineKeyboardButton("💎 BUY XP (Show UPI)", callback_data='show_upi')],
        [InlineKeyboardButton("🔙 Menu", callback_data='main_menu')]
    ]
    await query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))

async def handle_shop_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    if query.data == 'show_upi':
        upi_txt = f"💸 **ADD MONEY**\n\nUPI ID:\n`{settings.ADMIN_UPI}`\n\n(Tap to Copy)\nSend screenshot to Admin."
        await query.edit_message_text(upi_txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='menu_shop')]]), parse_mode='Markdown')
        return

    item = query.data.split('|')[1]
    uid = query.from_user.id
    user = db.get_user(uid, "")
    price = settings.PRICES.get(item, 50)
    
    if user['xp'] >= price:
        new_inv = user['inventory']
        new_inv[item] = new_inv.get(item, 0) + 1
        db.update_user(uid, {"inventory": new_inv}, inc_dict={"xp": -price}, transaction=f"Bought {item}")
        await query.answer(f"✅ Bought {item}!")
        await open_shop_menu(update, context)
    else:
        await query.answer("❌ Not enough XP!", show_alert=True)

# --- BANK ---
async def open_bank_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    u = db.get_user(query.from_user.id, "")
    limit = int(u.get('total_deposit', 0) * 0.5)
    
    txt = f"🏦 **BANK**\n👛 Wallet: {u['xp']}\n🔐 Bank: {u['bank']}\n📉 Loan Limit: {limit}"
    
    kb = [
        [InlineKeyboardButton("📥 Dep 50%", callback_data='bank_act|dep_50'),
         InlineKeyboardButton("📥 Dep 100%", callback_data='bank_act|dep_100')],
        [InlineKeyboardButton("📤 With 50%", callback_data='bank_act|with_50'),
         InlineKeyboardButton("📤 With 100%", callback_data='bank_act|with_100')],
        [InlineKeyboardButton("💸 Take Loan", callback_data='bank_act|loan')],
        [InlineKeyboardButton("🔙 Menu", callback_data='main_menu')]
    ]
    await query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))

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
            await q.answer(f"✅ Deposited {amount} XP")
        else:
            await q.answer("❌ Empty Wallet")
            
    elif 'with' in act:
        percent = 0.5 if '50' in act else 1.0
        amount = int(u['bank'] * percent)
        if amount > 0:
            db.update_user(uid, None, inc_dict={'xp': amount, 'bank': -amount})
            await q.answer(f"✅ Withdrawn {amount} XP")
        else:
            await q.answer("❌ Empty Bank")
            
    elif act == 'loan':
        limit = int(u.get('total_deposit', 0) * 0.5)
        if u['loan_amount'] > 0:
            await q.answer("❌ Pay old loan first!", show_alert=True)
        elif u['xp'] > 10 or u['bank'] > 10:
            await q.answer("❌ You have money! No loan.", show_alert=True)
        elif limit < 50:
            await q.answer("❌ Deposit history too low.", show_alert=True)
        else:
            db.update_user(uid, {"loan_amount": limit}, inc_dict={'xp': limit}, transaction="Loan Taken")
            await q.answer(f"✅ Loan of {limit} XP Approved!")
            
    await open_bank_menu(update, context)