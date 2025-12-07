import pymongo
import certifi
import datetime
import SETTINGS_AUR_PRICES as settings

# ==============================================================================
#  🔌 DATABASE CONNECTION
# ==============================================================================
try:
    client = pymongo.MongoClient(settings.MONGO_URI, tlsCAFile=certifi.where())
    db = client[settings.DB_NAME]
    
    users_collection = db["users"]
    bets_collection = db["active_bets"]
    
    # Create Index for speed
    bets_collection.create_index([("status", 1), ("game", 1)])
    
    print("✅ DATABASE: Connected successfully!")
except Exception as e:
    print(f"❌ DATABASE ERROR: {e}")
    users_collection = None
    bets_collection = None

# ==============================================================================
#  👤 USER MANAGEMENT
# ==============================================================================

def get_user(user_id, name):
    if users_collection is None: return None
    user_id = int(user_id)
    
    user = users_collection.find_one({"_id": user_id})

    if not user:
        new_user = {
            "_id": user_id,
            "username": name,
            "real_name": "Unknown",
            "gender": "Unknown",
            "city": "Unknown",
            "mobile": "Unknown",
            "is_registered": False,
            "reg_step": None,
            "xp": 0,             
            "bank": 0,           
            "total_deposit": 0,
            "loan_amount": 0,    
            "inventory": {"shield": 0, "double_xp": 0, "hint": 0, "fifty": 0, "skip": 0},
            "stats": {"wins": 0, "loss": 0, "games_played": 0},
            "history": [],
            "joined_date": datetime.datetime.now(),
            "is_banned": False
        }
        users_collection.insert_one(new_user)
        return new_user

    # Auto-Repair Logic
    updates = {}
    if "total_deposit" not in user: updates["total_deposit"] = 0
    if "is_banned" not in user: updates["is_banned"] = False
    
    if updates:
        users_collection.update_one({"_id": user_id}, {"$set": updates})
        user.update(updates)
        
    return user

def update_user(user_id, update_dict=None, inc_dict=None, transaction=None):
    user_id = int(user_id)
    query = {}
    
    if update_dict: query["$set"] = update_dict
    if inc_dict: query["$inc"] = inc_dict
    
    if transaction:
        query["$push"] = {
            "history": {
                "$each": [{"msg": transaction, "date": datetime.datetime.now()}],
                "$slice": -15 
            }
        }

    if query and users_collection is not None:
        users_collection.update_one({"_id": user_id}, query)

# ==============================================================================
#  🏇 BETTING & LEADERBOARD
# ==============================================================================

def save_bet(user_id, game_name, market, selection, amount):
    bet_data = {
        "user_id": user_id,
        "game": game_name,       
        "market": market,        # e.g., 'DISAWAR'
        "selection": int(selection),  
        "amount": int(amount),
        "status": "pending",     
        "date": datetime.datetime.now()
    }
    if bets_collection is not None:
        bets_collection.insert_one(bet_data)

def get_pending_bets(game_name, market):
    """Fetch pending bets for a specific market"""
    if bets_collection is None: return []
    return list(bets_collection.find({
        "game": game_name, 
        "market": market, 
        "status": "pending"
    }))

def mark_bet_processed(bet_id, status):
    if bets_collection is not None:
        bets_collection.update_one({"_id": bet_id}, {"$set": {"status": status}})