from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import SETTINGS_AUR_PRICES as settings
import DATABASE_MEMORY as db

def is_admin(user_id):
    # Check if ID is in list (Convert both to str to be safe, then match)
    return int(user_id) in settings.ADMIN_IDS

async def open_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    if not is_admin(uid): 
        await query.answer("❌ Chal be! Tu Admin nahi hai.", show_alert=True)
        return

    txt = f"⚙️ **ADMIN PANEL**\n👑 Boss ID: `{uid}`"
    kb = [
        [InlineKeyboardButton("💰 ADD XP", callback_data='admin_ask|add_xp'), 
         InlineKeyboardButton("✂️ CUT XP", callback_data='admin_ask|cut_xp')],
        [InlineKeyboardButton("👤 CHECK USER", callback_data='admin_ask|check_user'),
         InlineKeyboardButton("🚫 BAN USER", callback_data='admin_ask|ban_user')],
        [InlineKeyboardButton("🐎 HORSE RESULT", callback_data='admin_act|set_horse')],
        [InlineKeyboardButton("🎛 PLAYER MODE", callback_data='admin_player_view')]
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
        await query.edit_message_text("🏆 **Result kiske liye dena hai?**", reply_markup=InlineKeyboardMarkup(kb))
        
    elif data.startswith('admin_res|'):
        market = data.split('|')[1]
        context.user_data['resolving_market'] = market
        await query.edit_message_text(f"🏁 **{market}**\n\nWinning Number (0-99) likho chat mein:")
        context.user_data['admin_action'] = 'resolve_horse'

    elif data.startswith('admin_ask|'):
        action = data.split('|')[1]
        context.user_data['admin_action'] = action
        await query.edit_message_text(f"⌨️ **ACTION: {action.upper()}**\n\nAb **User ID** likho chat mein:")

async def process_admin_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return False
    
    action = context.user_data.get('admin_action')
    if not action: return False
    
    txt = update.message.text.strip()
    
    # Handle Horse Result
    if action == 'resolve_horse':
        market = context.user_data.get('resolving_market')
        try:
            win_num = int(txt)
            bets = db.get_pending_bets("Horse", market)
            count = 0
            for bet in bets:
                uid = bet['user_id']
                if bet['selection'] == win_num:
                    amt = bet['amount'] * settings.PAYOUTS['horse_win']
                    db.update_user(uid, None, inc_dict={"xp": amt}, transaction=f"Won Horse {market}")
                    db.mark_bet_processed(bet['_id'], "won")
                    await context.bot.send_message(uid, f"🐎 **JACKPOT!**\n{market} Result: {win_num}\nWon: {amt} XP")
                    count += 1
                else:
                    db.mark_bet_processed(bet['_id'], "lost")
            await update.message.reply_text(f"✅ Result Declared: {market} -> {win_num}\n🏆 Winners: {count}")
        except ValueError:
            await update.message.reply_text("❌ Number daal bhai!")
        context.user_data['admin_action'] = None
        return True

    # Handle User Actions
    try:
        # Step 1: Get Target ID
        if 'target_uid' not in context.user_data:
            target_id = int(txt)
            # Verify user exists (Allow Admin self-select)
            if not db.get_user(target_id, "") and target_id not in settings.ADMIN_IDS:
                await update.message.reply_text("❌ User DB mein nahi hai.")
                return True
            
            context.user_data['target_uid'] = target_id
            
            if action == 'check_user':
                u = db.get_user(target_id, "")
                await update.message.reply_text(f"🕵️ **REPORT:**\nID: {target_id}\nXP: {u['xp']}\nBank: {u['bank']}\nInv: {u['inventory']}")
                context.user_data['admin_action'] = None
            elif action == 'ban_user':
                db.update_user(target_id, {"is_banned": True})
                await update.message.reply_text(f"🚫 User {target_id} BANNED.")
                context.user_data['admin_action'] = None
            else:
                await update.message.reply_text(f"🔢 **Amount batao** ({action}):")
                # Don't clear action, wait for amount
        
        # Step 2: Get Amount (for XP add/cut)
        else:
            amt = int(txt)
            uid = context.user_data['target_uid']
            
            if action == 'add_xp':
                db.update_user(uid, None, inc_dict={"xp": amt}, transaction="Admin Gift")
                await update.message.reply_text(f"✅ Added {amt} XP to {uid}")
            elif action == 'cut_xp':
                db.update_user(uid, None, inc_dict={"xp": -amt}, transaction="Admin Fine")
                await update.message.reply_text(f"✂️ Cut {amt} XP from {uid}")
            
            context.user_data['admin_action'] = None
            del context.user_data['target_uid']

    except ValueError:
        await update.message.reply_text("❌ Number likh bhai, English nahi.")
        
    return True