from pymongo import MongoClient
import time

class DataRetriever:
    def __init__(self, db_name="conversniper", collection_name="social_data"):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def fetch_recent_posts(self):
        """Fetch all posts from MongoDB without a time window."""
        posts = self.collection.find()  # No time filter
        return posts

    def stream_data(self, poll_interval=5):  # Reduced from 60 to 5 seconds
        """Yield content, sentiment, post_id, and platform from MongoDB with adjustable polling."""
        while True:
            print(f"Checking MongoDB for new posts...")  # Debug print
            posts = self.fetch_recent_posts()
            count = 0
            seen = set()
            for post in posts:
                if post.get("_id") in seen:
                    continue
                seen.add(post.get("_id"))
                
                content = post.get("content", "")
                sentiment = post.get("sentiment", "Neutral")  
                platform = post.get("source", "Reddit")
                if sentiment == 'Neutral' or post.get("support", 0) < 100:
                    continue
                
                id = post.get("_id")  
                yield (content, sentiment, id, platform)
                count += 1
            if count == 0:
                print("No posts found in social_data collection!") 
            time.sleep(poll_interval)  # Check every 5 seconds

if __name__ == "__main__":
    retriever = DataRetriever()
    posts = retriever.fetch_recent_posts()
    print(f"Cursor: {posts}")
    count = 0
    for post in posts:
        count += 1
    if count == 0:
        print("No posts found in social_data collection!")