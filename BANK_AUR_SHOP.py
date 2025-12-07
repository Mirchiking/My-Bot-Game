from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import DATABASE_MEMORY as db
import SETTINGS_AUR_PRICES as settings

async def open_shop_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = db.get_user(query.from_user.id, "")
    
    txt = f"🛍️ **SHOP** | XP: {user['xp']}\n\n👇 **Powerups (50 XP each):**"
    kb = [
        [InlineKeyboardButton("💡 Hint", callback_data='shop_buy|hint'),
         InlineKeyboardButton("🛡️ Shield", callback_data='shop_buy|shield')],
        [InlineKeyboardButton("💎 BUY XP (Calculator)", callback_data='start_calc_xp')],
        [InlineKeyboardButton("🔙 Menu", callback_data='main_menu')]
    ]
    await query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))

async def handle_shop_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
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

# --- CALCULATOR ---
async def start_xp_calculator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['waiting_for_calc'] = True
    await update.callback_query.edit_message_text("🧮 **XP CALCULATOR**\n\nEnter Amount in ₹ (e.g. 50):")

async def process_xp_calculation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amt_inr = int(update.message.text)
        xp = int(amt_inr * 10) # ₹10 = 100 XP
        
        txt = f"🧾 **ESTIMATE**\n\n💸 Pay: ₹{amt_inr}\n💎 Get: {xp} XP\n\nUPI: `your-upi-id@okicici`\nSend screenshot to Admin."
        await update.message.reply_text(txt, parse_mode='Markdown')
        context.user_data['waiting_for_calc'] = False
    except:
        await update.message.reply_text("❌ Invalid number. Try again.")

# --- BANK ---
async def open_bank_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    u = db.get_user(query.from_user.id, "")
    limit = int(u.get('total_deposit', 0) * 0.5)
    
    txt = f"🏦 **BANK**\n👛 Wallet: {u['xp']}\n🔐 Bank: {u['bank']}\n📉 Loan: {u['loan_amount']}/{limit}"
    kb = [
        [InlineKeyboardButton("📥 Deposit All", callback_data='bank_action|dep'),
         InlineKeyboardButton("📤 Withdraw All", callback_data='bank_action|with')],
        [InlineKeyboardButton("💸 Take Loan", callback_data='bank_action|loan')],
        [InlineKeyboardButton("🔙 Menu", callback_data='main_menu')]
    ]
    await query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))

async def handle_bank_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    act = q.data.split('|')[1]
    uid = q.from_user.id
    u = db.get_user(uid, "")
    
    if act == 'dep':
        if u['xp'] > 0:
            db.update_user(uid, None, inc_dict={'xp': -u['xp'], 'bank': u['xp']})
            await q.answer("✅ Deposited")
    elif act == 'with':
        if u['bank'] > 0:
            db.update_user(uid, None, inc_dict={'xp': u['bank'], 'bank': -u['bank']})
            await q.answer("✅ Withdrawn")
    elif act == 'loan':
        limit = int(u.get('total_deposit', 0) * 0.5)
        if u['loan_amount'] > 0:
            await q.answer("❌ Clear existing loan first!", show_alert=True)
        elif u['xp'] > 10 or u['bank'] > 10:
            await q.answer("❌ You have money! No loan.", show_alert=True)
        elif limit < 50:
            await q.answer("❌ Deposit history too low.", show_alert=True)
        else:
            db.update_user(uid, {"loan_amount": limit}, inc_dict={'xp': limit}, transaction="Loan Taken")
            await q.answer(f"✅ Loan of {limit} XP Approved!")
            
    await open_bank_menu(update, context)