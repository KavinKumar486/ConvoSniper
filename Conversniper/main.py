#main.py
import logging
logging.getLogger("prawcore").setLevel(logging.ERROR)
import redis
import threading
import asyncio
import time
from redit import RedditSniper
from discord_sniper import DiscordSniper
from analyze_sentiment import SentimentAnalyzer
from backend import Backend
from analytics_engine import AnalyticsEngine
from Generate_response.response_generator import ResponseGenerator  # Import the class

class ConversniperControl:
    def __init__(self):
        self.cache = redis.Redis(host='localhost', port=6379, db=0)
        self.reddit_sniper = RedditSniper(self.cache)
        self.discord_sniper = DiscordSniper(self.cache)
        self.backend = Backend()
        self.sentiment_analyzer = SentimentAnalyzer(self.cache, self.backend.store_data)
        self.analytics_engine = AnalyticsEngine()  # Re-enable analytics engine if needed
        self.response_generator = ResponseGenerator()  # Initialize ResponseGenerator

    def start_reddit(self):
        print("Launching Reddit sniper...")
        self.reddit_sniper.run()

    def start_discord(self):
        print("Launching Discord sniper...")
        asyncio.run(self.discord_sniper.run())

    def start_analyzer(self):
        print("Launching Sentiment Analyzer...")
        self.sentiment_analyzer.analyze()

    def start_analytics(self):
        print("Launching Analytics Engine...")
        self.analytics_engine.run()

    def start_response_generator(self):
        print("Launching Response Generator...")
        self.response_generator.run()

    def get_stored_responses(self, post_id=None, limit=10):
        """Retrieve stored responses for further processing."""
        return self.response_generator.get_responses(post_id=post_id, limit=limit)

    def run(self):
        # Start all components in threads
        reddit_thread = threading.Thread(target=self.start_reddit, daemon=True)
        reddit_thread.start()
        
        discord_thread = threading.Thread(target=self.start_discord, daemon=True)
        discord_thread.start()
        
        analytics_thread = threading.Thread(target=self.start_analytics, daemon=True)
        analytics_thread.start()
        
        response_generator_thread = threading.Thread(target=self.start_response_generator, daemon=True)
        response_generator_thread.start()
        
        self.start_analyzer()
        
        try:
            time.sleep(86400)  # 24 hours (adjust as needed)
        except KeyboardInterrupt:
            print("Shutting down ConversniperControl...")

if __name__ == "__main__":
    controller = ConversniperControl()
    controller.run()