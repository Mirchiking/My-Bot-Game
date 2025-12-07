from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import SETTINGS_AUR_PRICES as settings
import DATABASE_MEMORY as db

def is_admin(user_id):
    return user_id in settings.ADMIN_IDS

async def open_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    if not is_admin(uid): return

    total_users = db.get_all_users_count()
    
    txt = f"⚙️ **ADMIN DASHBOARD**\n👑 Master: {uid}\n👥 Total Users: {total_users}"
    kb = [
        [InlineKeyboardButton("👤 My Profile", callback_data='show_profile')],
        [InlineKeyboardButton("👥 Check User", callback_data='admin_ask|check_user'),
         InlineKeyboardButton("🔄 Reset User", callback_data='admin_ask|reset_user')],
        [InlineKeyboardButton("💰 Add XP", callback_data='admin_ask|add_xp'), 
         InlineKeyboardButton("✂️ Cut XP", callback_data='admin_ask|cut_xp')],
        [InlineKeyboardButton("🐎 DECLARE RESULT", callback_data='admin_act|set_horse')],
        [InlineKeyboardButton("🎛 Switch to Player", callback_data='main_menu')],
        [InlineKeyboardButton("🔙 Exit", callback_data='main_menu')]
    ]
    await query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def handle_admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data.startswith('admin_act|set_horse'):
        kb = []
        for m in settings.MARKETS.keys():
            kb.append([InlineKeyboardButton(f"🏁 {m}", callback_data=f'admin_res|{m}')])
        kb.append([InlineKeyboardButton("🔙 Back", callback_data='admin_dashboard')])
        await query.edit_message_text("🏆 **Select Market to Declare Result:**", reply_markup=InlineKeyboardMarkup(kb))
        
    elif data.startswith('admin_ask|'):
        action = data.split('|')[1]
        context.user_data['admin_action'] = action
        await query.edit_message_text(f"⌨️ **ACTION: {action.upper()}**\n\nSend the **User ID** now (Type in chat):")

async def process_admin_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles manual Admin inputs like User IDs for XP/Reset"""
    if not is_admin(update.effective_user.id): return False
    
    action = context.user_data.get('admin_action')
    if not action: return False
    
    try:
        target_id = int(update.message.text)
        target_user = db.get_user(target_id, "")
        
        if not target_user['is_registered']:
            await update.message.reply_text("❌ User not found or not registered.")
            context.user_data['admin_action'] = None
            return True

        if action == 'check_user':
            u = target_user
            msg = f"🕵️ **USER REPORT**\nID: `{u['_id']}`\nName: {u['real_name']}\nXP: {u['xp']}\nBank: {u['bank']}\nInv: {u['inventory']}"
            await update.message.reply_text(msg, parse_mode='Markdown')
            
        elif action == 'reset_user':
            db.reset_user_data(target_id)
            await update.message.reply_text(f"♻️ **User {target_id} has been RESET.**")
            
        elif action == 'add_xp':
            context.user_data['target_uid'] = target_id
            context.user_data['admin_action'] = 'confirm_add_xp'
            await update.message.reply_text(f"💰 Adding XP to **{target_id}**.\nEnter Amount:")
            return True
            
        elif action == 'cut_xp':
            context.user_data['target_uid'] = target_id
            context.user_data['admin_action'] = 'confirm_cut_xp'
            await update.message.reply_text(f"✂️ Cutting XP from **{target_id}**.\nEnter Amount:")
            return True
            
        elif action == 'confirm_add_xp':
            amt = int(update.message.text)
            uid = context.user_data['target_uid']
            db.update_user(uid, None, inc_dict={"xp": amt, "total_deposit": amt}, transaction="Admin Add")
            await update.message.reply_text(f"✅ Added {amt} XP to {uid}.")
            await context.bot.send_message(uid, f"🎁 **Admin Added:** {amt} XP")
            
        elif action == 'confirm_cut_xp':
            amt = int(update.message.text)
            uid = context.user_data['target_uid']
            db.update_user(uid, None, inc_dict={"xp": -amt}, transaction="Admin Cut")
            await update.message.reply_text(f"✂️ Cut {amt} XP from {uid}.")
            await context.bot.send_message(uid, f"📉 **Admin Deducted:** {amt} XP")

        # Reset State
        context.user_data['admin_action'] = None
        return True
        
    except ValueError:
        await update.message.reply_text("❌ Invalid Number. Action Cancelled.")
        context.user_data['admin_action'] = None
        return True

# --- RESULT DECLARATION ---
async def handle_market_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    market = query.data.split('|')[1]
    context.user_data['resolving_market'] = market
    await query.edit_message_text(f"🏁 **Resolving: {market}**\n\nType the Winning Number (0-99) using command:\n`/result {market} NUMBER`")

async def resolve_market_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    try:
        market = context.args[0].upper()
        win_num = int(context.args[1])
    except:
        await update.message.reply_text("❌ Usage: `/result MARKET NUMBER`")
        return

    bets = db.get_pending_bets("Horse", market)
    total_paid = 0
    count = 0
    
    for bet in bets:
        uid = bet['user_id']
        amt = bet['amount']
        
        if bet['selection'] == win_num:
            win_amt = amt * settings.PAYOUTS['horse_win']
            db.update_user(uid, None, inc_dict={"xp": win_amt}, transaction=f"Won {market}")
            db.mark_bet_processed(bet['_id'], "won")
            try: await context.bot.send_message(uid, f"🎉 **YOU WON!**\nMarket: {market}\nNumber: {win_num}\nWon: {win_amt} XP")
            except: pass
            total_paid += win_amt
            count += 1
        else:
            db.mark_bet_processed(bet['_id'], "lost")
            
    await update.message.reply_text(f"✅ **RESULT DECLARED: {market}**\n🏆 Winner: {win_num}\n👥 Winners: {count}\n💰 Paid: {total_paid} XP")