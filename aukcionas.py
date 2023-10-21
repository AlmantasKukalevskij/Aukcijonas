from pymongo import MongoClient
import json
client = MongoClient("localhost", 27017)

db = client.auction_db

bids_collection = db.bids

persons = db.persons
users = db.users
items = db.items
bids = db.bids
auctions = db.auctions
statuses = db.statuses

#pridedam zmogu
person_data = {"fname": "Jonas", "lname": "Jonaitis"}
persons.insert_one(person_data)

#Pridedam zmogu kaip vartotoja
user_data = {"personId": person_data['_id'], "username":"Jogaila", "email":"jonas.jonaitis@vu.lt"}
user_insert_result = users.insert_one(user_data)

#Sukuriam itema susijusi (ikelta) userio
item_data = {
    "userId": user_insert_result.inserted_id,
    "title": "Auksinis Charizardas",
    "description": "Kortele kurioje yra paveikslelis, bet ji kainuoja daugiau negu namas",
    "status": "listed"
}
item_insert_result = items.insert_one(item_data)

auction_data = {
    "itemId": item_insert_result.inserted_id, #referencina itema kuris tik ka buvo sukurtas
    "startTime": "2023-10-20T12:00:00",
    "finishTime": "2023-10-27t12:00:00",
    "status": "listed",
    "bids": [
        {"userId": user_insert_result.inserted_id, "amount":100, "timeStamp":"2023-10-20T13:00:00"}
    ]
}
auctions.insert_one(auction_data)



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