import pymongo
import certifi
import datetime
import SETTINGS_AUR_PRICES as settings

# RAM Cache (Speed ke liye)
user_cache = {}

# --- DATABASE CONNECTION ---
try:
    client = pymongo.MongoClient(settings.MONGO_URI, tlsCAFile=certifi.where())
    db = client[settings.DB_NAME]
    users_collection = db["users"]
    
    # Connection Check
    client.admin.command('ping')
    print("✅ DATABASE: Cloud Connected (MongoDB Atlas)!")
    
except Exception as e:
    print(f"❌ DATABASE ERROR: Connect nahi hua.\nReason: {e}")
    users_collection = None

# --- MAIN FUNCTIONS ---

def get_user(user_id, name):
    """
    User ka data lata hai. Agar naya user hai to naye fields ke sath banata hai.
    """
    user_id = int(user_id)
    
    # 1. Check RAM Cache
    if user_id in user_cache:
        return user_cache[user_id]

    if users_collection is None:
        return None

    # 2. Database Query
    user = users_collection.find_one({"_id": user_id})

    # 3. New User Creation (Agar pehli baar aaya hai)
    if not user:
        new_user = {
            "_id": user_id,
            "username": name,         # Telegram Name
            
            # --- NEW REGISTRATION FIELDS ---
            "real_name": "Unknown",   # Asli Naam
            "gender": "Unknown",      # Male/Female
            "city": "Unknown",        # Shahar
            "mobile": "Unknown",      # Paytm/UPI Number
            "is_registered": False,   # Registration complete hai ya nahi
            "reg_step": None,         # Abhi form ke kis step par hai
            # -------------------------------

            "xp": 0,             
            "bank": 0,           
            "lifetime_xp": 0,    
            "loan_amount": 0,    
            "inventory": {"shield": 0, "double_xp": 0, "hint": 0, "fifty": 0, "skip": 0},
            "stats": {"wins": 0, "loss": 0, "games_played": 0},
            "history": [],
            "joined_date": datetime.datetime.now()
        }
        users_collection.insert_one(new_user)
        user_cache[user_id] = new_user
        print(f"🆕 NEW PLAYER JOINED: {name}")
        return new_user

    # 4. AUTO-REPAIR (Agar purane user ke paas naye features nahi hain)
    needs_fix = False
    
    # Ye fields check karega, agar nahi mile to add karega
    default_values = {
        "real_name": "Unknown",
        "gender": "Unknown",
        "city": "Unknown",
        "mobile": "Unknown",
        "is_registered": True, # Purane users ko registered manenge
        "reg_step": None,
        "bank": 0,
        "inventory": {"shield": 0, "double_xp": 0, "hint": 0, "fifty": 0, "skip": 0},
        "stats": {"wins": 0, "loss": 0, "games_played": 0}
    }

    for key, value in default_values.items():
        if key not in user:
            user[key] = value
            needs_fix = True

    if needs_fix:
        users_collection.update_one({"_id": user_id}, {"$set": user})
        print(f"🛠️ REPAIRED DATA for {name}")

    # Save to Cache
    user_cache[user_id] = user
    return user

def update_user(user_id, update_dict, inc_dict=None, transaction=None):
    """
    User data update karta hai.
    """
    user_id = int(user_id)
    query = {}
    
    if update_dict:
        query["$set"] = update_dict
        
    if inc_dict:
        query["$inc"] = inc_dict
        
    if transaction:
        query["$push"] = {
            "history": {
                "$each": [{"msg": transaction, "date": datetime.datetime.now()}],
                "$slice": -10 
            }
        }

    if query and users_collection is not None:
        users_collection.update_one({"_id": user_id}, query)
        
        # Cache delete karte hain taaki next time fresh data aaye
        if user_id in user_cache:
            del user_cache[user_id]