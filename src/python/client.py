import discord_module as discord

import asyncio
import discord
from discord.ext import commands
import pymongo

import config

class OUT_Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.database_client = pymongo.MongoClient(kwargs["mongodb_uri"])
        self.discord_database = self.database_client["discord"]

        self.hypixel_key = kwargs["hypixel_key"]

    async def setup_hook(self):
        for cog in config.cogs:
            await self.load_extension(f"cogs.{cog}")

        await self.tree.sync(guild=discord.Object(id=503560012581568514))

    async def close(self):
        await super().close()
        await self.close()

    def insert_database_user(self, user_id):
        database_collection = self.get_database_collection("users")

        database_collection.insert_one({
            "_id": user_id,
            "outcoins": 0,
            "events": 0,
            "badges": [],
            "chatgames": 0,
            "messages": 0,
            "uuid": None,
            "supporting": None,
            "emote": None
        })

    def get_database_collection(self, collection):
        return self.discord_database[collection]

    async def database_user_preload(self, user_id):
        database_count = self.get_database_collection("users").count_documents({"_id": user_id})

        if database_count > 1:
            emergency_embed = self.create_embed(
                "Database Emergency",
                "There are duplicate entries in the database that could lead to future data corruption.",
                config.embed_error_color
            )

            emergency_embed.add_field(name="User ID", value=user_id)

            staff_channel = self.get_channel(config.channel_ids["staff_announcements"])
            await staff_channel.send(embed=emergency_embed)
            return await staff_channel.send("<@!348311499946721282>")

        if database_count == 0:
            self.insert_database_user(user_id)

    async def fetch_member(self, user_id):
        guild = await self.fetch_guild(503560012581568514)

        try: member = await guild.fetch_member(user_id)
        except discord.NotFound: member = OUT_Bot_Member(user_id, guild)

        return member

    @staticmethod
    def create_embed(title, description, color):
        return OUT_Bot_Embed(title, description, color)

    @staticmethod
    def has_role(member, role):
        member_roles = list(map(lambda member_role: member_role.name, member.roles))
        return role in member_roles

    async def message_response(self, message, member, timeout):
        def check_message(to_check):
            if to_check.channel != message.channel:
                return False
            if to_check.author != member:
                return False

            return True

        try:
            return await self.wait_for("message", check=check_message, timeout=timeout)
        except asyncio.TimeoutError:
            return None

    async def message_reaction(self, message, member, timeout):
        def check_reaction(reaction, user):
            if reaction.message != message:
                return False
            if user != member:
                return False

            return True

        try:
            return str((await self.wait_for("reaction_add", check=check_reaction, timeout=timeout))[0].emoji)
        except asyncio.TimeoutError:
            return None

    @staticmethod
    def has_more_authority(guild, member_1, member_2):
        role_1 = member_1.roles[-1]
        role_2 = member_2.roles[-1]

        if guild.roles.index(role_1) > guild.roles.index(role_2):
            return True

        return False

    @staticmethod
    def decode_duration(duration):
        time_conversions = {
            "s": 1,
            "m": 60,
            "h": 3600,
            "d": 86400
        }

        if duration[-1] not in list(time_conversions.keys()):
            return None

        duration_unit = time_conversions[duration[-1]]

        try:
            duration_quantity = int(duration[:-1])
        except ValueError:
            return None

        return duration_quantity * duration_unit

class OUT_Bot_Avatar:
    def __init__(self):
        self.key = "avatar"
        self.url = "https://cdn.discordapp.com/embed/avatars/0.png"

class OUT_Bot_Member:
    def __init__(self, user_id, guild):
        self.avatar = OUT_Bot_Avatar()
        self.bot = False
        self.guild = guild
        self.id = user_id
        self.mention = "OldMember#0000"
        self.name = "OldMember"
        self.roles = []

class OUT_Bot_Embed(discord.Embed):
    def __init__(self, title, description, color):
        super().__init__(title=title, description=description, color=color)
        self.set_author(
            name="OUT Bot",
            icon_url="https://cdn.discordapp.com/avatars/735989802822008893/dccdfc83ab30e8d86e39224fe84875b4.webp"
        )

        self.set_thumbnail(url="https://cdn.discordapp.com/banners/503560012581568514/e42b1c7a86fe10b995be98d718e81d16.jpg")
