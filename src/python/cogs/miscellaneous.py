import discord_module as discord

from asyncio import sleep, TimeoutError
from datetime import datetime, timedelta
import discord
from discord.ext import commands
from json import load
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
            command_embed = self.client.create_embed("OUT Help Page", "The command you just ran was used incorrectly.", config.embed_error_color)
            command_embed.add_field(name=command["usage"],
                                    value=f"Required Roles: `{', '.join(command['required_roles'])}`\nAliases: `{', '.join(command['aliases']) if len(command['aliases']) > 0 else 'None'}`",
                                    inline=True)
            command_embed.set_footer(text=f"Created by: {command['signature']}")

            return await ctx.reply(embed=command_embed)
        elif isinstance(error, commands.CommandError):
            error_embed = self.client.create_embed("Command Raised Error", "The command you attempted to run produced an unexpected error, it will be closely analyzed by our staff.", config.embed_error_color)
            await ctx.reply(embed=error_embed)

            line = format_exception(type(error), error, error.__traceback__)[2].lstrip()
            log_embed = self.client.create_embed("Command Raised Error", f"```{error}```\n```py\n{line}```\n", config.embed_error_color)
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
            member = self.client.get_user(348311499946721282)
            check = starbuck_check
        elif "moth" in message.content.lower():
            member = self.client.get_user(273890943407751168)
            check = moth_check
        else: return

        if len(list(filter(check, self.client.cached_messages))) > 3: return
        channel = await member.create_dm()
        return await channel.send(f"Somebody has mentioned you in {message.channel.mention}!")

    launchcat_details = command_details["launchcat"]

    @commands.command(name="launchcat",
                      aliases=launchcat_details["aliases"],
                      usage=launchcat_details["usage"],
                      description=launchcat_details["description"],
                      signature=launchcat_details["signature"])
    @commands.has_any_role(*launchcat_details["required_roles"])
    @commands.cooldown(launchcat_details["cooldown_rate"], launchcat_details["cooldown_per"])
    async def launchcat(self, ctx):
        launchcat_embed = self.client.create_embed("Launch Cat Has Been Summoned!", "Kneel before this great ancient power!", config.embed_success_color)
        launchcat_embed.set_image(url="https://i.ibb.co/48GL17V/ezgif-6-e88e29c7c266.gif")
        return await ctx.reply(embed=launchcat_embed)

    birthday_details = command_details["birthday"]

    @commands.command(name="birthday",
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

async def setup(client):
    await client.add_cog(Miscellaneous(client), guilds=[discord.Object(id=503560012581568514)])
