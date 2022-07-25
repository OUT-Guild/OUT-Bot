import discord_module as discord

import discord
from dotenv import load_dotenv
from os import getenv

from client import OUT_Bot

if __name__ == "__main__":
    load_dotenv()

    client = OUT_Bot(command_prefix="!", intents=discord.Intents.all(), case_insensitive=True, help_command=None,
                     mongodb_uri=getenv("MONGODB_URI"), hypixel_key=getenv("HYPIXEL_KEY"))
    client.run(getenv("BOT_TOKEN"))

self.client.get_database_collection("users")
user_collection.update_many({}, {"$unset": {"lastMessage": 1, "votes": 1, "timesSaid": 1, "characterCountStarted": 1, "characters": 1, "lastMuteEvent": 1, "username": 1}, "$rename": {"eventsWon": "events"}, "$set": {"uuid": None, "emote": None}}, {"multi": True})
await ctx.send("Whew!")
