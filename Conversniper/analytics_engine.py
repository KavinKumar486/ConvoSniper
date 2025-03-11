#analytics_engine.py
from pymongo import MongoClient
import time
import random
import numpy as np
# from generate_response.response_generator import ResponseGenerator  # Commented out

class AnalyticsEngine:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["conversniper"]
        self.collection = self.db["social_data"]
        self.seen_posts = set()
        # self.response_generator = ResponseGenerator()  

    def analyze_trends(self):
        """Analyze trends from last 10 minutes, filter fresh posts."""
        time_threshold = time.time() - 600
        posts = list(self.collection.find({"stored_at": {"$gte": time_threshold}}))
        
        if not posts:
            return None, None
        
        new_posts = [post for post in posts if post["content"] not in self.seen_posts]
        if not new_posts:
            return None, None
        
        for post in new_posts:
            support = post.get("support", 0)
            comment_count = post.get("comment_count", 0)
            sentiment_score = post.get("sentiment_score", 0.5)
            post["trend_score"] = support + comment_count * 2 + sentiment_score * 10
            self.seen_posts.add(post["content"])
        
        trending = sorted(new_posts, key=lambda x: x["trend_score"], reverse=True)[:5]
        return trending, new_posts

    def generate_post(self, trending):
        """Generate a placeholder reaction message (no NLP response for now)."""
        if not trending:
            return "Yo Python & datascience crew—what’s hot today? Spill your wildest ideas! 🔥"
        
        top_post = random.choice(trending)
        source = top_post["source"]
        community = "r/python+datascience" if source == "Reddit" else "this server"
        content = top_post["content"]
        
        return f"Trending on {community}: {content} — let’s discuss this gem!"

    def run(self):
        print("Analytics Engine online—sniping trends every minute from MongoDB...")
        while True:
            trending, all_posts = self.analyze_trends()
            if trending:
                reaction_post = self.generate_post(trending)
                
            else:
                print("No fresh trending data—waiting for new community sparks!")
            time.sleep(60)