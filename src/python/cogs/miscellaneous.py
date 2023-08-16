import discord_module as discord

from asyncio import sleep, TimeoutError
from datetime import datetime, timedelta
import discord
from discord.ext import commands
from json import load
from random import choice
from string import ascii_uppercase
from traceback import format_exception

import config

class Miscellaneous(commands.Cog):
    with open("command_details.json", "r") as json_file:
        command_details = load(json_file)

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, TimeoutError) or isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRole) or isinstance(error, commands.MissingAnyRole):
            return await ctx.reply("L")
        elif isinstance(error, commands.MissingRequiredArgument):
            command = self.command_details[ctx.command.name]

            command_embed = self.client.create_embed(
                "OUT Help Page",
                "The command you just ran was used incorrectly.",
                config.embed_error_color
            )

            command_embed.add_field(
                name=command["usage"],
                value=f"Required Roles: `{', '.join(command['required_roles'])}`\nAliases: `{', '.join(command['aliases']) if len(command['aliases']) > 0 else 'None'}`",
                inline=True
            )

            command_embed.set_footer(text=f"Created by: {command['signature']}")

            return await ctx.reply(embed=command_embed)
        elif isinstance(error, commands.CommandError):
            error_embed = self.client.create_embed(
                "Command Raised Error",
                "The command you attempted to run produced an unexpected error, it will be closely analyzed by our staff.",
                config.embed_error_color
            )

            await ctx.reply(embed=error_embed)

            formatted_exception = format_exception(type(error), error, error.__traceback__)
            line = f"{formatted_exception[2].lstrip()}"

            log_embed = self.client.create_embed(
                "Command Raised Error",
                f"An exception occured while trying to execute **!{ctx.command.name}**.",
                config.embed_error_color
            )

            log_embed.add_field(name="Error Traceback", value=f"```{error}```\n```py\n{line}```\n", inline=True)

            log_embed.set_footer(text=error.__class__.__name__)

            log_channel = self.client.get_channel(config.channel_ids["miscellaneous_logs"])
            return await log_channel.send(embed=log_embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.category.id == config.category_ids["ingame"]: return

        def starbuck_check(cached_message):
            if cached_message.author.id == 348311499946721282: return False
            if cached_message.author != message.author: return False
            if ((datetime.now(tz=cached_message.created_at.tzinfo) + timedelta(seconds=1)) - cached_message.created_at).seconds >= 300: return False
            if "starbuck" not in cached_message.content.lower(): return False
            return True

        def moth_check(cached_message):
            if cached_message.author.id == 273890943407751168: return False
            if cached_message.author != message.author: return False
            if ((datetime.now(tz=cached_message.created_at.tzinfo) + timedelta(seconds=1)) - cached_message.created_at).seconds >= 300: return False
            if "moth" not in cached_message.content.lower(): return False
            return True

        if "starbuck" in message.content.lower():
            if message.author.id == 348311499946721282: return
            member = self.client.get_user(348311499946721282)
            check = starbuck_check
        elif "moth" in message.content.lower():
            if message.author.id == 273890943407751168: return
            member = self.client.get_user(273890943407751168)
            check = moth_check
        else: return

        if len(list(filter(check, self.client.cached_messages))) > 3: return
        channel = await member.create_dm()
        return await channel.send(f"Somebody has mentioned you in {message.channel.mention}!")

    launchcat_details = command_details["launchcat"]

    @commands.command(
        name="launchcat",
        aliases=launchcat_details["aliases"],
        usage=launchcat_details["usage"],
        description=launchcat_details["description"],
        signature=launchcat_details["signature"])
    @commands.has_any_role(*launchcat_details["required_roles"])
    @commands.cooldown(launchcat_details["cooldown_rate"], launchcat_details["cooldown_per"])
    async def launchcat(self, ctx):
        launchcat_embed = self.client.create_embed(
            "Launch Cat Has Been Summoned!",
            "Kneel before this great ancient power!",
            config.embed_success_color
        )

        launchcat_embed.set_image(url="https://i.ibb.co/48GL17V/ezgif-6-e88e29c7c266.gif")
        return await ctx.reply(embed=launchcat_embed)

    birthday_details = command_details["birthday"]

    @commands.command(
        name="birthday",
        aliases=birthday_details["aliases"],
        usage=birthday_details["usage"],
        description=birthday_details["description"],
        signature=birthday_details["signature"])
    @commands.has_any_role(*birthday_details["required_roles"])
    @commands.cooldown(birthday_details["cooldown_rate"], birthday_details["cooldown_per"])
    async def birthday(self, ctx, member: discord.Member, member_name, channel: discord.TextChannel):
        await sleep(2)
        await channel.send(member.mention)

        song_lines = [
            f"Happy Birthday to you!",
            f"Happy Birthday to you!",
            f"Happy Birthday, dear {member_name}!",
            f"Happy Birthday to you!"
        ]

        await sleep(10)
        for song_line in song_lines:
            await channel.send(song_line)
            await sleep(4)

        await self.client.database_user_preload(member.id)
        user_collection = self.client.get_database_collection("users")

        user_collection.update_one({"_id": member.id}, {"$inc": {"outcoins": 15000}})
        return await channel.send("Enjoy the OUT Coins :D")
    
    viewcollage_details = command_details["viewcollage"]

    @commands.command(
        name="viewcollage",
        aliases=viewcollage_details["aliases"],
        usage=viewcollage_details["usage"],
        description=viewcollage_details["description"],
        signature=viewcollage_details["signature"])
    @commands.has_any_role(*viewcollage_details["required_roles"])
    @commands.cooldown(viewcollage_details["cooldown_rate"], viewcollage_details["cooldown_per"])
    async def viewcollage(self, ctx, member: discord.Member):
        collage_collection = self.client.get_database_collection("collages")
        collages = collage_collection.find({"member": member.id})

        if collages.count() == 0:
            clean_collage_embed = self.client.create_embed(
                "Clean Collage",
                f"{member.mention} has no embarrassing images to showcase.",
                config.embed_success_color
            )

            return await ctx.reply(embed=clean_collage_embed)
        
        loading_data_embed = self.client.create_embed(
            "Loading Data",
            "Currently fetching data from our database...",
            config.embed_info_color
        )

        page_index = 0
        message = await ctx.reply(embed=loading_data_embed)

        while True:
            collage = collages[page_index]

            collage_embed = self.client.create_embed(
                f"{member.display_name}'s Collage",
                "*embarrassingggg...*",
                config.embed_success_color
            )

            collage_embed.add_field(name="Submitted By", value=f"<@!{collage['submitter']}>", inline=True)
            collage_embed.add_field(name="Collage Image ID", value=collage["_id"], inline=True)
            collage_embed.set_image(url=collage["image"])
            collage_embed.set_footer(text=f"Image {page_index + 1}/{collages.count()}")

            await message.edit(embed=collage_embed)
            await message.add_reaction("⏮")
            await message.add_reaction("⬅")
            await message.add_reaction("🛑")
            await message.add_reaction("➡")
            await message.add_reaction("⏭")

            collage_reply = await self.client.message_reaction(message, ctx.author, 150)

            if collage_reply is None:
                return

            async def invalid_response():
                invalid_response_embed = self.client.create_embed(
                    "Invalid Response",
                    "The response that you provided to the question was not acceptable.",
                    config.embed_error_color
                )

                await message.edit(embed=invalid_response_embed)

            if collage_reply not in ["⏮", "⬅", "🛑", "➡", "⏭"]:
                return await invalid_response()

            await message.remove_reaction(collage_reply, ctx.author)

            if collage_reply == "⏮":
                page_index = 0
            elif collage_reply == "⬅":
                page_index -= 1
            elif collage_reply == "🛑":
                await message.remove_reaction("⏮", ctx.guild.me)
                await message.remove_reaction("⬅", ctx.guild.me)
                await message.remove_reaction("🛑", ctx.guild.me)
                await message.remove_reaction("➡", ctx.guild.me)
                await message.remove_reaction("⏭", ctx.guild.me)
                return
            elif collage_reply == "➡":
                page_index += 1
            elif collage_reply == "⏭":
                page_index = collages.count() - 1

            if page_index == -1:
                page_index = collages.count() - 1

            if page_index == collages.count():
                page_index = 0

    addcollage_details = command_details["addcollage"]

    @commands.command(
        name="addcollage",
        aliases=addcollage_details["aliases"],
        usage=addcollage_details["usage"],
        description=addcollage_details["description"],
        signature=addcollage_details["signature"])
    @commands.has_any_role(*addcollage_details["required_roles"])
    @commands.cooldown(addcollage_details["cooldown_rate"], addcollage_details["cooldown_per"])
    async def addcollage(self, ctx, member: discord.Member):
        if len(ctx.message.attachments) == 0:
            no_attachment_embed = self.client.create_embed(
                "No Attachment",
                "You did not attach an image to your message.",
                config.embed_error_color
            )

            return await ctx.reply(embed=no_attachment_embed)
        
        collage_collection = self.client.get_database_collection("collages")

        for attachment in ctx.message.attachments:
            while True:
                collage_id = "".join([choice(ascii_uppercase) for _ in range(6)])

                if collage_collection.find({"_id": collage_id}).count() == 0:
                    collage_collection.insert_one({
                        "_id": collage_id,
                        "member": member.id,
                        "submitter": ctx.author.id,
                        "image": attachment.url
                    })

                    break

        collage_added_embed = self.client.create_embed(
            "Collage Added",
            f"Successfully added {len(ctx.message.attachments)} image(s) to {member.mention}'s collage.",
            config.embed_success_color
        )

        return await ctx.reply(embed=collage_added_embed)
    
    removecollage_details = command_details["removecollage"]

    @commands.command(
        name="removecollage",
        aliases=removecollage_details["aliases"],
        usage=removecollage_details["usage"],
        description=removecollage_details["description"],
        signature=removecollage_details["signature"])
    @commands.has_any_role(*removecollage_details["required_roles"])
    @commands.cooldown(removecollage_details["cooldown_rate"], removecollage_details["cooldown_per"])
    async def removecollage(self, ctx, collage_id: str):
        collage_collection = self.client.get_database_collection("collages")
        collage = collage_collection.find_one({"_id": collage_id})

        if collage is None:
            invalid_collage_embed = self.client.create_embed(
                "Invalid Collage",
                "The collage ID that you provided is invalid.",
                config.embed_error_color
            )

            return await ctx.reply(embed=invalid_collage_embed)
        
        collage_collection.delete_one({"_id": collage_id})

        collage_removed_embed = self.client.create_embed(
            "Collage Removed",
            f"Successfully removed {collage_id} from {collage['member']}'s collage.",
            config.embed_success_color
        )

        return await ctx.reply(embed=collage_removed_embed)

async def setup(client):
    await client.add_cog(Miscellaneous(client), guilds=[discord.Object(id=503560012581568514)])
