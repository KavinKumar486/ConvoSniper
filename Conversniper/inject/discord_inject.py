import logging
logging.getLogger("prawcore").setLevel(logging.ERROR)
import discord
import asyncio

class DiscordInjector: 
    def __init__(self):
        self.token = "MTM0Mzg2ODAwOTg2ODk1MTU4Mg.Gq7bx9.mqusCiMc-i2OiZNWr9K3A4dTBCI_1xF7-Y-4Nw"  # Your bot’s token
        intents = discord.Intents.default()  # Define intents
        intents.message_content = True       # Enable message content intent
        self.client = discord.Client(intents=intents)  # Pass intents to Client
        self.channel_id = 1344097588063764550  # Your working Discord channel ID

    async def on_ready(self):
        print(f"Logged in as {self.client.user}")
        channel = self.client.get_channel(self.channel_id)
        if channel:
            try:
                await channel.send("Hey crew, AI’s lit! Let’s vibe on this with DataScienceCo!")
                print(f"Posted to Discord channel {self.channel_id}")
            except Exception as e:
                print(f"Failed to post: {e}")
        else:
            print(f"Channel ID {self.channel_id} not found!")
        await self.client.close()  # Close after posting

    async def run(self):
        print("🚀 Discord injector test mode activated!\n")
        self.client.event(self.on_ready) 
        await self.client.start(self.token)

if __name__ == "__main__":
    injector = DiscordInjector()
    asyncio.run(injector.run())