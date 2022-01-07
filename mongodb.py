import pymongo

myclient = pymongo.MongoClient()

db = myclient["db"]

users = db["users"]

rooms = db["rooms"]

online = db["online"]

chats = db["chats"]

files = db["files"]
