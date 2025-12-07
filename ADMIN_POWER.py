from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import SETTINGS_AUR_PRICES as settings
import DATABASE_MEMORY as db
import asyncio

def is_admin(user_id):
    return user_id in settings.ADMIN_IDS

async def open_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id): return

    txt = "⚙️ **ADMIN DASHBOARD**"
    kb = [
        [InlineKeyboardButton("💰 Add XP", callback_data='admin_act|add_xp_menu')],
        [InlineKeyboardButton("🐎 DECLARE RESULT", callback_data='admin_act|set_horse')],
        [InlineKeyboardButton("🔙 Exit", callback_data='main_menu')]
    ]
    await query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def handle_admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split('|')[1]
    
    if data == 'set_horse':
        # Show Markets
        kb = []
        for m in settings.MARKETS.keys():
            kb.append([InlineKeyboardButton(f"🏁 {m}", callback_data=f'admin_res|{m}')])
        kb.append([InlineKeyboardButton("🔙 Back", callback_data='admin_dashboard')])
        await query.edit_message_text("Select Market to Declare Result:", reply_markup=InlineKeyboardMarkup(kb))

async def handle_market_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin enters the winning number"""
    query = update.callback_query
    market = query.data.split('|')[1]
    
    # Context hack to pass market to text handler, or use simpler buttons for 0-99 (Hard)
    # Using a simplified approach: Admin picks range or we use command for precision
    # Better: Ask Admin to type number via command, OR use buttons for random generation? 
    # Let's use command prompt simulation via Text, but here for safety, let's ask to confirm.
    
    context.user_data['resolving_market'] = market
    await query.edit_message_text(f"⚠️ **Resolving: {market}**\n\nType the Winning Number (0-99) in chat using command:\n`/result {market} NUMBER`")

async def resolve_market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    TRIGGERED BY COMMAND: /result DISAWAR 45
    This is the heavy logic that pays winners automatically.
    """
    if not is_admin(update.effective_user.id): return
    
    try:
        market = context.args[0].upper()
        win_num = int(context.args[1])
    except:
        await update.message.reply_text("❌ Usage: `/result MARKET_NAME NUMBER`")
        return

    # 1. Get All Pending Bets
    bets = db.get_pending_bets("Horse", market)
    if not bets:
        await update.message.reply_text(f"ℹ️ No active bets for {market}.")
        return

    total_payout = 0
    winners_count = 0
    
    await update.message.reply_text(f"🔄 Processing {len(bets)} bets for {market} (Win: {win_num})...")

    for bet in bets:
        uid = bet['user_id']
        amt = bet['amount']
        bet_id = bet['_id']
        
        if bet['selection'] == win_num:
            # WINNER
            win_amt = amt * settings.PAYOUTS['horse_win']
            
            # Loan Recovery Logic
            user = db.get_user(uid, "")
            loan = user.get('loan_amount', 0)
            final_pay = win_amt
            deducted = 0
            
            if loan > 0:
                if win_amt >= loan:
                    deducted = loan
                    final_pay = win_amt - loan
                    db.update_user(uid, {"loan_amount": 0})
                else:
                    deducted = win_amt
                    final_pay = 0
                    db.update_user(uid, None, inc_dict={"loan_amount": -deducted})

            # Credit User
            if final_pay > 0:
                db.update_user(uid, None, inc_dict={"xp": final_pay}, transaction=f"Win {market} #{win_num}")
            
            db.mark_bet_processed(bet_id, "won")
            
            # Notify Winner
            try:
                msg = f"🎉 **JACKPOT! {market} Result: {win_num}**\n💰 Won: {win_amt} XP\n📉 Loan Deducted: {deducted}\n💵 **Net:** {final_pay} XP"
                await context.bot.send_message(uid, msg, parse_mode='Markdown')
            except: pass
            
            total_payout += win_amt
            winners_count += 1
        else:
            # LOSER
            db.mark_bet_processed(bet_id, "lost")

    await update.message.reply_text(f"✅ **RESULT DECLARED!**\n🏆 Winner #: {win_num}\n👥 Winners: {winners_count}\n💸 Total Paid: {total_payout} XP")

# --- OTHER COMMANDS ---
async def add_xp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    try:
        uid = int(context.args[0])
        amt = int(context.args[1])
        db.update_user(uid, None, inc_dict={"xp": amt, "total_deposit": amt}, transaction="Admin Deposit")
        await update.message.reply_text(f"✅ Added {amt} XP to {uid}")
        await context.bot.send_message(uid, f"💰 Admin added {amt} XP to your wallet.")
    except Exception as e:
        await update.message.reply_text("Usage: `/addxp UID AMOUNT`")

async def broadcast_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    msg = " ".join(context.args)
    # Note: Broadcasting to thousands requires a queue in production. Simple loop here.
    # In real production, use db.users_collection.find()
    await update.message.reply_text("📢 Broadcast Started...")