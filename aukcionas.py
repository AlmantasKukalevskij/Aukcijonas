from pymongo import MongoClient
import json
from datetime import datetime

def add_user(db, fname, lname, username, email):
    # Sukuriamas zmogus (person)
    person_data = {"fname": fname, "lname": lname}
    db.persons.insert_one(person_data)

    # Pridedamas zmogus kaip vartotojas (user)
    user_data = {"personId": person_data['_id'], "username": username, "email": email}
    user_insert_result = db.users.insert_one(user_data)

    return user_insert_result

def add_item(db, user_id, title, description, status="listed"):
    item_data = {
        "userId": user_id,
        "title": title,
        "description": description,
        "status": status
    }
    item_insert_result = db.items.insert_one(item_data)
    return item_insert_result

def bid_on_auction(db, auction_id, user_id, amount):
    # Gauname aukcijona pagal ID
    auction = db.auctions.find_one({"_id": auction_id})

    # Patikrinam ar aukcijonas vis dar vyksta
    current_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    if auction["startTime"] <= current_time <= auction["finishTime"]:
        
        # Sukuriamas naujas pasiulymas
        bid = {
            "userId": user_id,
            "amount": amount,
            "timeStamp": current_time
        }

        # Iterpiam ta pasiulyma i aukcijono bidu sarasa
        auction["bids"].append(bid)

        # Atnaujinam aukcijona
        db.auctions.update_one({"_id": auction_id}, {"$set": {"bids": auction["bids"]}})
        return bid
    else:
        print("Aukcijonas nebevyksta!")
        return None
    
def create_auction(db, item_id, user_id, start_time, finish_time, amount):
    auction_data = {
        "itemId": item_id,
        "startTime": start_time,
        "finishTime": finish_time,
        "status": "listed",
        "bids": [{"userId": user_id, "amount": amount, "timeStamp": start_time}]
    }
    auction_insert_result = db.auctions.insert_one(auction_data)
    return db.auctions.find_one({"_id": auction_insert_result.inserted_id})



client = MongoClient("localhost", 27017)

db = client.auction_db

bids_collection = db.bids

persons = db.persons
users = db.users
items = db.items
bids = db.bids
auctions = db.auctions
statuses = db.statuses

user_result = add_user(db, "Jonas", "Jonaitis", "Jogaila", "jonas.jonaitis@vu.lt")
print("User added with ID:", user_result.inserted_id)

#Sukuriam itema susijusi (ikelta) userio
item_result = add_item(db, user_result.inserted_id, "Auksinis Charizardas", "Kortele kurioje yra paveikslelis, bet ji kainuoja daugiau negu namas")
print("Item added with ID:", item_result.inserted_id)

#auction_data = {
#    "itemId": item_result.inserted_id, #referencina itema kuris tik ka buvo sukurtas
#    "startTime": "2023-10-20T12:00:00",
#    "finishTime": "2023-10-27t12:00:00",
#    "status": "listed",
#    "bids": [
#        {"userId": user_result.inserted_id, "amount":100, "timeStamp":"2023-10-20T13:00:00"}
#    ]
#}

#sukuriam aukcijona
auction_data = create_auction(
    db,
    item_result.inserted_id,
    user_result.inserted_id,
    "2023-10-20T12:00:00",
    "2023-10-27t12:00:00",
    100
)

#auctions.insert_one(auction_data)

auction_id = auction_data["_id"]  # Cia turetu buti aukcijono id, kuriame norime dalyvauti
new_bid = bid_on_auction(db, auction_id, user_result.inserted_id, 150)
if new_bid:
    print("Pasiulymas sekmingai pateiktas")
else:
    print ("Pasiulymas nebuvo pateiktas")







#nuskaito i jsona
# gaunam TIK embeded bids fielda is visu aukcijonu
bids_only = list(auctions.find({}, {"bids": 1, "_id": 0}))

# Extract embedded bids from all auctions
all_bids = []
for auction in bids_only:
    all_bids.extend(auction["bids"])

# Since the userId is stored as an ObjectId, convert it to a string for JSON serialization
for bid in all_bids:
    bid["userId"] = str(bid["userId"])

# Saugom i jsona
with open("bids.json", "w") as file:
    json.dump(all_bids, file, indent=4)

print("Data exported to bids.json")