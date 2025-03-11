import asyncio
from inject.reddit_inject import RedditInjector
from inject.discord_inject import DiscordInjector  # Assuming this exists
import time
import logging
logging.getLogger("prawcore").setLevel(logging.ERROR)

class MainInjector:
    def __init__(self):
        self.reddit_injector = RedditInjector()
        self.discord_injector = DiscordInjector()

    async def inject_response(self, response, platform):
        """Inject a response to the specified platform."""
        print(f"🚀 Injecting response to {platform}...\n")
        
        if platform == "Reddit":
            self.reddit_injector.post(response)
            print(f"Completed Reddit injection.")
        
        elif platform == "Discord":
            await self.discord_injector.start_and_post(1343148141905711188, response)
            print(f"Completed Discord injection.")
        
        else:
            print(f"Unknown platform: {platform}. Skipping injection.")

    async def run(self):
        """Run the injector to post a test response."""
        response = "Hey crew, AI’s lit! Let’s vibe on this with DataScienceCo!"
        platform = "Reddit"  # For testing
        await self.inject_response(response, platform)
        time.sleep(3)

if __name__ == "__main__":
    injector = MainInjector()
    asyncio.run(injector.run())