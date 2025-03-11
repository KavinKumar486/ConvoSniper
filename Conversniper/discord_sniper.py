# discord_sniper.py
import logging
logging.getLogger("prawcore").setLevel(logging.ERROR)
import discord
from discord.ext import commands
import redis
from datetime import datetime, timedelta

class DiscordSniper:
    def __init__(self, cache):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        self.bot = commands.Bot(command_prefix="!", intents=intents)
        self.cache = cache
        self.time_cutoff = datetime.utcnow() - timedelta(hours=24)
        
        @self.bot.event
        async def on_ready():
            print(f"Logged in as {self.bot.user}")
        
        @self.bot.event
        async def on_message(message):
            if message.author == self.bot.user:
                return
            
            msg_time = message.created_at.replace(tzinfo=None)
            if msg_time < self.time_cutoff:
                return
            
            msg_data = {
                "id": str(message.id),
                "content": message.content,
                "channel": str(message.channel),
                "reactions": sum(r.count for r in message.reactions),
                "source": "Discord",
                "timestamp": msg_time.timestamp()
            }
            self.cache.set(f"discord:{msg_data['id']}", str(msg_data))  # Cache all messages
            

        @self.bot.event
        async def on_reaction_add(reaction, user):
            message = reaction.message
            msg_time = message.created_at.replace(tzinfo=None)
            if msg_time < self.time_cutoff or message.author == self.bot.user:
                return
            
            msg_data = {
                "id": str(message.id),
                "content": message.content,
                "channel": str(message.channel),
                "reactions": sum(r.count for r in message.reactions),
                "source": "Discord",
                "timestamp": msg_time.timestamp()
            }
            self.cache.set(f"discord:{msg_data['id']}", str(msg_data))  # Update cache on react
            

    async def run(self):
        await self.bot.start("MTM0MzEzMjI5MTA2ODcyNzM4Nw.GoT1Ul.3yYySm7-f-4l-f2jjo_F-jmpsWKmwDcH6M6OuA")