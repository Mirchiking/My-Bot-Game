import random

# --- HINGLISH DIALOGUES & RULES ---

GREETINGS = [
    "Aur Boss! Kya haal hain? 😎",
    "Swagat hai Gaming Ke Baap ke pass! 👑",
    "Aaja Bhai, aaj tera din hai! 🚀",
    "Paisa hi Paisa hoga aaj toh! 💰",
    "Oye Champion! Ready hai na? 🥊"
]

TITLES = {
    'noob': "👶 Noobda (Level 0)",
    'pro': "😎 Khiladi (Level 10+)",
    'legend': "🦁 Sher (Level 50+)",
    'god': "⚡ Bhagwan (Level 100+)"
}

TEXTS = {
    # Onboarding
    'welcome_dm': """
{greeting} **{name}**! 👋

🆔 **User ID:** `{user_id}`
🏅 **Rank:** {rank}
💎 **Jeb Mein:** {xp} XP
🏦 **Bank Mein:** {bank} XP

Main hoon **Mystery Bot**. Yahan sirf XP chalta hai!
Jeetoge toh Raja 👑, Haaroge toh... Try Again! 😅

Batao kya karna hai? 👇
""",

    'group_welcome': """
👋 **Oye {name}! Welcome to the Gang!** Yahan sirf chill mahol hai.
Game khelna hai aur XP kamana hai toh **DM mein aao**.
Warna yahan baith ke tamasha dekho! 😂

👇 **Niche Button dabao aur DM mein aao:**
""",

    # Rules
    'rules_general': """
📜 **NIYAM AUR KANOON (Rules)** 📜

1. **XP = Izzat:** Jitna XP, utni izzat. 0 XP matlab khatam tata bye bye.
2. **Bank Use Karo:** Game khelne se pehle Paisa Bank mein daalo, warna haarne pe sab ud jayega.
3. **No Cheating:** Agar spam kiya ya bot ko confuse kiya, toh seedha **BAN**.
4. **Loan:** Sirf tab milega jab wallet aur bank dono 0 honge.
5. **Respect:** Bot se pyaar se baat karo, warna reply nahi milega.

_Samajh gaye? Toh khelo dil khol ke!_
""",

    'rules_snake': "🐍 **SNAKE RULES:**\n- Ungli se (Swipe) control karo.\n- Deewar (Wall) se mat takrana.\n- Khud ko mat kaatna.\n- Har Apple = 2 XP.",
    'rules_horse': "🐎 **HORSE RACING:**\n- 0 se 99 koi bhi Number chuno.\n- Jitne chaho utne ghodo par paisa lagao.\n- Result time par aayega.\n- Jeete toh 90x Paisa!",
    'rules_bowl': "🎱 **LUCKY BOWL:**\n- 1 se 5 Number select karo.\n- Agar ball tumhare number pe ruki... JACKPOT (90x)!\n- Risk hai toh ishq hai!",

    # Game Results
    'win_hype': [
        "🎉 **ARRE WAAH!** Party kab de raha hai? 🍻",
        "🚀 **Udd gaya paisa!** Jeet gaye Guru!",
        "🤑 **Note chaap diye bhai ne!**",
        "👑 **System Hila Diya!** Big Win!"
    ],
    
    'loss_funny': [
        "💔 **Dil se bura lagta hai bhai...** Haar gaye.",
        "📉 **Gareebi aa gayi...** Koi nahi, loan lele!",
        "🤣 **Bot se jeetna mushkil hi nahi, namumkin hai!**",
        "🧹 **Safaya ho gaya!** Better luck next time."
    ],
    
    # Bank & Shop
    'insufficient': "❌ **Bhai Jeb Khali Hai!**\nPehle XP kamao ya Bank se nikalo. Udhaar nahi chalta yahan.",
    'loan_taken': "💸 **Le Bhai Karza!**\nAb ye XP wapis bhi karna hai, bhool mat jana.",
    'shop_success': "✅ **Item Kharid Liya!**\nAb game mein use karna mat bhoolna."
}

def get_random_greeting(): return random.choice(GREETINGS)
def get_rank_name(xp):
    if xp < 1000: return TITLES['noob']
    elif xp < 5000: return TITLES['pro']
    elif xp < 20000: return TITLES['legend']
    return TITLES['god']