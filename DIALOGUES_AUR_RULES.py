import random

# ==============================================================================
#  ADVANCED DIALOGUES & RULES ENGINE
#  Tone: Funny, Emotional, Respectful, Hinglish
# ==============================================================================

# --- 1. RANDOM GREETINGS (Har baar naya welcome) ---
GREETINGS_LIST = [
    "Namaste",
    "Radhe Radhe",
    "Oye Champion",
    "Aur Mere Bhai",
    "Welcome Back",
    "Aagaye Aap",
    "Jai Hind"
]

# --- 2. RANK / CATEGORIES SYSTEM (As per your request) ---
# Format: 'key': 'Display Name'
RANK_TITLES = {
    'noob': "👶 Noob (Level 0)",
    'pro': "😎 Pro (Level 10+)",
    'legend': "👑 Legend (Level 50+)",
    'god': "⚡ God Mode (Level 100+)"
}

# --- 3. ICONS & EMOJIS ---
ICONS = {
    'xp': "💎",
    'bank': "🏦",
    'shop': "🛒",
    'warn': "⚠️",
    'game': "🎮",
    'loan': "💸",
    'time': "⏳"
}

# --- 4. MAIN MESSAGES DICTIONARY ---

TEXTS = {
    # --- WELCOME MESSAGE (Personal DM) ---
    'welcome_dm': """
{greeting} **{name}**! 👋

🆔 **User ID:** `{user_id}`
🏅 **Rank:** {rank}
💎 **XP Wallet:** {xp} XP

Main hoon aapka Gaming Buddy! 🤖
Game khelo Group mein, par hisaab-kitaab hoga yahan DM mein.

Kiya karna chahenge aaj? Niche buttons dabao! 👇
""",

    # --- TIME RESTRICTION (10 AM - 9 PM) ---
    'shop_closed': """
😴 **Sone ka time hai Bhai!**

Humari gaming shop sirf **Subah 10 baje se Raat 9 baje** tak khulti hai.
Abhi bot aaram kar raha hai. Kal subah aana, tab tak energy bacha ke rakho! 🌙

_Time abhi: {current_time}_
""",

    # --- GROUP WELCOME (First Time Join) ---
    'group_welcome': """
👋 **Swagat hai {name} Gaming Arena mein!**

Aapko milte hain **Joining Bonus: {bonus} XP**! 🎁
Aap abhi **{rank}** level par ho.

Game khelne ke liye taiyaar ho jao! Result sabko yahan dikhega, par prize aapke DM mein aayega.
""",

    # --- RULES (Funny & Clear) ---
    'game_rules': """
📜 **NIYAM AUR SHARTEIN (Rules)** 📜

1. **🚫 No Typing:** Yahan likhna mana hai, sirf Buttons dabane ka!
2. **💎 XP is Money:** Game jeeto, XP kamao. Yehi aapki currency hai.
3. **🏦 Bank System:** Apne XP Bank mein save karo warna game haarne par udd jayenge.
4. **🤝 Loan Suvidha:** Agar kangal ho gaye (0 XP), tabhi Loan milega.
5. **🤬 Respect:** Gaali-galoch nahi, hum yahan sirf fun ke liye hain.

_Samajh gaye? Toh chalo shuru karte hain!_
""",

    # --- BANK MESSAGES ---
    'bank_menu': """
🏦 **XP BANK OF GAMERS**

Yahan aapke XP safe rahenge.
💰 **Wallet Balance:** {wallet} XP
🔐 **Bank Balance:** {bank} XP
📉 **Loan Active:** {loan_status}

Kya karna hai Seth ji? 👇
""",
    
    'deposit_success': "✅ **Jama Ho Gaye!** {amount} XP ab Bank mein safe hain.",
    'withdraw_success': "✅ **Nikaal Liye!** {amount} XP aapke Wallet mein aa gaye.",
    'insufficient_funds': "❌ **Garib ho kya?** Itne XP toh hai hi nahi tumhare paas! 😅",
    
    # --- SHOP & LIFELINES ---
    'shop_menu': """
🛒 **MAGIC SHOP**
Apne XP se power-ups kharido aur game mein dominance banao!

1. 🛡️ **XP Shield:** Haarne par XP nahi katenge.
2. 🚀 **Double Dhamaka:** Jeetne par 2x profit.
3. 🤞 **Luck Booster:** Dice game mein jeetne ke chance badh jayenge.

_Select karo niche se:_
""",

    # --- GAME RESULTS ---
    'win_msg': "🎉 **Badhai ho!** Aap jeet gaye **{amount} XP**! Party kab de rahe ho?",
    'lose_msg': "💔 **Oh No!** Aap haar gaye **{amount} XP**. Koi baat nahi, agli baar pakka jeetoge!",
    
    # --- LOAN ---
    'loan_approved': "✅ **Loan Approved!** {amount} XP de diye hain. Time pe chuka dena warna byaaj (interest) lagega!",
    'loan_rejected': "❌ **Loan Rejected!** Pehle purana hisaab clear karo ya wallet 0 hone ka wait karo."
}

# --- 5. HELPER FUNCTIONS (Logic ko asaan banane ke liye) ---

def get_random_greeting():
    """Returns a random greeting string"""
    return random.choice(GREETINGS_LIST)

def get_rank_name(xp):
    """Returns rank name based on XP/Level logic"""
    # Logic: XP ke hisaab se rank decide karega
    if xp < 1000:
        return RANK_TITLES['noob']
    elif xp < 5000:
        return RANK_TITLES['pro']
    elif xp < 20000:
        return RANK_TITLES['legend']
    else:
        return RANK_TITLES['god']