# backend.py (unchanged)
from pymongo import MongoClient
import time

class Backend:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["conversniper"]
        self.collection = self.db["social_data"]

    def store_data(self, data):
        data["stored_at"] = time.time()
        try:
            self.collection.insert_one(data)
    
        except Exception as e:
            print(f"MongoDB Error: {e}")

    def run(self):
        print("MongoDB backend ready...")