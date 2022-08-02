import discord_module as discord

import discord
from discord.ext import commands
from json import load

import config

class Badges(commands.Cog):
    with open("command_details.json", "r") as json_file:
        command_details = load(json_file)

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            await self.client.database_user_preload(message.author.id)
            user_collection = self.client.get_database_collection("users")
            user_collection.update_one({"_id": message.author.id}, {"$inc": {"messages": 1}})
            user_profile = user_collection.find_one({"_id": message.author.id})

            if user_profile["messages"] == 500:
                user_collection.update_one({"_id": message.author.id}, {"$push": {"badges": "messages_3"}})
            elif user_profile["messages"] == 2500:
                user_collection.update_one({"_id": message.author.id}, {"$pull": {"badges": "messages_3"}})
                user_collection.update_one({"_id": message.author.id}, {"$push": {"badges": "messages_2"}})
            elif user_profile["messages"] == 5000:
                user_collection.update_one({"_id": message.author.id}, {"$pull": {"badges": "messages_2"}})
                user_collection.update_one({"_id": message.author.id}, {"$push": {"badges": "messages_1"}})

            # TODO Chatgames

    events_details = command_details["events"]

    @commands.command(
        name="events",
        aliases=events_details["aliases"],
        usage=events_details["usage"],
        description=events_details["description"],
        signature=events_details["signature"]
    )
    @commands.has_any_role(*events_details["required_roles"])
    @commands.cooldown(events_details["cooldown_rate"], events_details["cooldown_per"])
    async def events(self, ctx, argument, amount: int, *args: discord.Member):
        argument = argument.lower()
        user_collection = self.client.get_database_collection("users")
        member_ids = list(map(lambda member: member.id, args))
        member_identifications = list(map(lambda member: f"{member.name} ({member.mention})", args))

        if argument in ["add", "inc"]:
            for member in args:
                await self.client.database_user_preload(member.id)

            user_collection.update_many({"_id": {"$in": member_ids}}, {"$inc": {"events": amount}})
            win_embed = self.client.create_embed(
                "Event Wins Added",
                "The respective member(s) have received their event wins.",
                config.embed_success_color
            )

            await ctx.reply(embed=win_embed)

            log_embed = self.client.create_embed(
                "Event Wins Added",
                "Event Wins have been distributed by a moderator.",
                config.embed_info_color
            )

            log_embed.add_field(name="Member(s)", value=", ".join(member_identifications), inline=True)
            log_embed.add_field(name="Moderator", value=f"{ctx.author.name} ({ctx.author.mention})")
            log_embed.add_field(name="Amount", value=f"{amount}", inline=False)

            log_channel = self.client.get_channel(config.channel_ids["miscellaneous_logs"])
            await log_channel.send(embed=log_embed)
        elif argument in ["subtract", "sub"]:
            for member in args:
                await self.client.database_user_preload(member.id)

            user_collection.update_many({"_id": {"$in": member_ids}}, {"$inc": {"events": -1 * amount}})
            coins_embed = self.client.create_embed(
                "Event Wins Removed",
                "The respective member(s) have been removed of their Event Wins.",
                config.embed_success_color
            )

            await ctx.reply(embed=coins_embed)

            log_embed = self.client.create_embed(
                "Event Wins Removed",
                "Event Wins have been taken by a moderator.",
                config.embed_info_color
            )

            log_embed.add_field(name="Member(s)", value=", ".join(member_identifications), inline=True)
            log_embed.add_field(name="Moderator", value=f"{ctx.author.name} ({ctx.author.mention})")
            log_embed.add_field(name="Amount", value=amount, inline=False)

            log_channel = self.client.get_channel(config.channel_ids["miscellaneous_logs"])
            await log_channel.send(embed=log_embed)
        else:
            argument_embed = self.client.create_embed(
                "Invalid Argument",
                "The argument that you provided was not acceptable.",
                config.embed_error_color
            )

            return await ctx.reply(embed=argument_embed)

        for member in args:
            user_profile = user_collection.find_one({"_id": member.id})

            if user_profile["eventsWon"] == 1:
                user_collection.update_one({"_id": member.id}, {"$push": {"badges": "event_3"}})
            elif user_profile["eventsWon"] == 3:
                user_collection.update_one({"_id": member.id}, {"$pull": {"badges": "event_3"}})
                user_collection.update_one({"_id": member.id}, {"$push": {"badges": "event_2"}})
            elif user_profile["eventsWon"] == 11:
                user_collection.update_one({"_id": member.id}, {"$pull": {"badges": "event_2"}})
                user_collection.update_one({"_id": member.id}, {"$push": {"badges": "event_1"}})

async def setup(client):
    await client.add_cog(Badges(client), guilds=[discord.Object(id=503560012581568514)])
