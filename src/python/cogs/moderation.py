import discord_module as discord

import discord
from discord.errors import Forbidden, NotFound
from discord.ext import commands
from emoji import demojize
from json import load
from random import choice
from string import ascii_uppercase
from time import time

import config

class Moderation(commands.Cog):
    with open("command_details.json", "r") as json_file:
        command_details = load(json_file)

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener(name="on_message")
    async def on_message(self, message):
        if message.author.bot or message.guild is None:
            return

        await self.client.database_user_preload(message.author.id)

        if self.client.has_role(message.author, "OUT Staff"):
            return

        for character in demojize(message.content):  # Translates all unicode emojis to their Discord form
            if character not in config.allowed_regex:
                await message.delete()

                notification_embed = self.client.create_embed("Invalid Character",
                                                              "Your recently sent message was deleted as our system detected an unknown character. Please understand that this is a new system and not every character has been indexed, this will not count as any form of warning or punishment on your record. If you believe that this character should be allowed, please contact <@!273890943407751168>.",
                                                              config.embed_info_color)

                notification_embed.add_field(name="Character In Question", value=f'"{character}"', inline=False)

                log_embed = self.client.create_embed("Invalid Character",
                                                     f"{message.author.name} ({message.author.mention}) sent an invalid character not known to our database and the message was deleted.",
                                                     config.embed_info_color)

                log_embed.add_field(name="Member In Question", value=f"{message.author.name} ({message.author.mention})",
                                    inline=False)
                log_embed.add_field(name="Character In Question", value=f'"{character}"', inline=True)

                user_dm = await message.author.create_dm()

                try:
                    await user_dm.send(embed=notification_embed)
                except Forbidden:  # The user has DMs disabled
                    log_embed.set_footer(text=f"{message.author.name} was not made aware on why their message was deleted as their DMs are disabled.")

                log_channel = self.client.get_channel(config.channel_ids["moderation"])
                return await log_channel.send(embed=log_embed)

    clear_details = command_details["clear"]

    @commands.command(name="clear",
                      aliases=clear_details["aliases"],
                      usage=clear_details["usage"],
                      description=clear_details["description"],
                      signature=clear_details["signature"])
    @commands.has_any_role(*clear_details["required_roles"])
    @commands.cooldown(clear_details["cooldown_rate"], clear_details["cooldown_per"])
    async def clear(self, ctx, number):
        await ctx.channel.purge(number)

        log_embed = self.client.create_embed("Channel Cleared",
                                             f"{ctx.channel.mention} was cleared of messages by {ctx.author.name} ({ctx.author.mention}).",
                                             config.embed_info_color)

        log_embed.add_field(name="Command Run by", value=f"{ctx.author.mention} ({ctx.author.name})", inline=False)
        log_embed.add_field(name="Cleared Channel", value=ctx.channel.mention, inline=True)
        log_embed.add_field(name="Number of Messages Cleared", value=number, inline=True)

        log_channel = self.client.get_channel(config.channel_ids["moderation"])
        return await log_channel.send(embed=log_embed)

    punish_details = command_details["punish"]

    @commands.command(name="punish",
                      aliases=punish_details["aliases"],
                      usage=punish_details["usage"],
                      description=punish_details["description"],
                      signature=punish_details["signature"])
    @commands.has_any_role(*punish_details["required_roles"])
    @commands.cooldown(punish_details["cooldown_rate"], punish_details["cooldown_per"])
    async def punish(self, ctx, member: discord.Member, *, reason="No Reason Given"):
        if not self.client.has_more_authority(ctx.guild, ctx.author, member):
            authority_embed = self.client.create_embed("Invalid Authority",
                                                       f"You lack the authority to punish {member.name} ({member.mention}).",
                                                       config.embed_error_color)

            return await ctx.reply(embed=authority_embed)

        warnings_collection = self.client.get_database_collection("warnings")

        while True:
            warning_id = "".join([choice(ascii_uppercase) for _ in range(6)])

            if warnings_collection.find({"_id": warning_id}).count() == 0:
                warnings_collection.insert_one({
                    "_id": warning_id,
                    "member": member.id,
                    "moderator": ctx.author.id,
                    "reason": reason,
                    "time": round(time())
                })

                notification_embed = self.client.create_embed("You Have Been Warned",
                                                              f"A moderator has warned you due to unruly behavior that is not tolerated. This is only a warning, but still be cautious of how you act in our server's environment.",
                                                              config.embed_info_color)

                notification_embed.add_field(name="Warning ID", value=warning_id, inline=True)
                notification_embed.add_field(name="Reason for Warning", value=reason, inline=False)

                user_dm = await member.create_dm()

                try:
                    await user_dm.send(embed=notification_embed)
                    notification_sent = True
                except Forbidden:  # The user has DMs disabled
                    notification_sent = False

                log_embed = self.client.create_embed("Warning Issued",
                                                     f"A warning was issued to {member.name} ({member.mention}) by a moderator.",
                                                     config.embed_info_color)

                log_embed.add_field(name="Warning ID", value=warning_id, inline=True)
                log_embed.add_field(name="Member in Question", value=f"{member.name} ({member.mention})", inline=False)
                log_embed.add_field(name="Warning Issued By", value=f"{ctx.author.name} ({ctx.author.mention})" ,inline=True)
                log_embed.add_field(name="Reason for Warning", value=reason, inline=False)

                if not notification_sent:
                    log_embed.set_footer(text="The member did not receive a notification because their DMs are disabled.")

                log_channel = self.client.get_channel(config.channel_ids["moderation"])
                await log_channel.send(embed=log_embed)

                success_embed = self.client.create_embed("Warning Issued",
                                                         f"Your warning to {member.name} ({member.mention}) was issued successfully.",
                                                         config.embed_success_color)

                success_embed.add_field(name="Warning ID", value=warning_id, inline=True)
                success_embed.add_field(name="Member in Question", value=f"{member.name} ({member.mention})", inline=False)
                success_embed.add_field(name="Reason for Warning", value=reason, inline=False)

                if not notification_sent:
                    success_embed.set_footer(text="The member did not receive a notification because their DMs are disabled.")

                return await ctx.reply(embed=success_embed)

    pardon_details = command_details["pardon"]

    @commands.command(name="pardon",
                      aliases=pardon_details["aliases"],
                      usage=pardon_details["usage"],
                      description=pardon_details["description"],
                      signature=pardon_details["signature"])
    @commands.has_any_role(*pardon_details["required_roles"])
    @commands.cooldown(pardon_details["cooldown_rate"], pardon_details["cooldown_per"])
    async def pardon(self, ctx, user: discord.User, warning_id, *, reason="No Reason Given"):
        warnings_collection = self.client.get_database_collection("warnings")

        if warnings_collection.find({"_id": warning_id, "member": user.id}).count() == 0:
            error_embed = self.client.create_embed("Warning Not Found",
                                                   "No warning with that ID was found in my database.",
                                                   config.embed_error_color)

            return await ctx.reply(embed=error_embed)

        warnings_collection.delete_one({"_id": warning_id})

        notification_embed = self.client.create_embed("Warning Pardoned",
                                                      "One of your warnings was pardoned by a moderator.",
                                                      config.embed_info_color)

        notification_embed.add_field(name="Warning ID", value=warning_id, inline=True)
        notification_embed.add_field(name="Pardon Reason", value=reason, inline=False)

        member_dm = await user.create_dm()

        try:
            await member_dm.send(embed=notification_embed)
            notification_sent = True
        except Forbidden:  # The user has DMs disabled
            notification_sent = False

        log_embed = self.client.create_embed("Warning Pardoned",
                                             "A warning was pardoned by a moderator.",
                                             config.embed_info_color)

        log_embed.add_field(name="Warning ID", value=warning_id, inline=True)
        log_embed.add_field(name="Moderator", value=f"{ctx.author.name} ({ctx.author.mention})", inline=False)
        log_embed.add_field(name="Pardon Reason", value=reason, inline=True)

        if not notification_sent:
            log_embed.set_footer(text="The member did not receive a notification because their DMs are disabled.")

        log_channel = self.client.get_channel(config.channel_ids["moderation"])
        await log_channel.send(embed=log_embed)

        success_embed = self.client.create_embed("Warning Pardoned Successfully",
                                                 "Your warning was successfully pardoned.",
                                                 config.embed_success_color)

        success_embed.add_field(name="Warning ID", value=warning_id, inline=True)
        success_embed.add_field(name="Pardon Reason", value=reason, inline=False)

        if not notification_sent:
            success_embed.set_footer(text="The member did not receive a notification because their DMs are disabled.")

        return await ctx.reply(embed=success_embed)

    warning_details = command_details["warning"]

    @commands.command(name="warning",
                      aliases=warning_details["aliases"],
                      usage=warning_details["usage"],
                      description=warning_details["description"],
                      signature=warning_details["signature"])
    @commands.has_any_role(*warning_details["required_roles"])
    @commands.cooldown(warning_details["cooldown_rate"], warning_details["cooldown_per"])
    async def warning(self, ctx, warning_id):
        warning_collection = self.client.get_database_collection("warnings")

        if warning_collection.find({"_id": warning_id}).count() == 0:
            error_embed = self.client.create_embed("Warning Not Found",
                                                   "No warning with that ID was found in my database.",
                                                   config.embed_error_color)

            return await ctx.reply(embed=error_embed)

        warning = warning_collection.find_one({"_id": warning_id})
        member = await self.client.fetch_member(warning["member"])
        moderator = await self.client.fetch_member(warning["moderator"])

        warning_embed = self.client.create_embed(
            "Warning Issued",
            f"A warning was issued to {member.name} ({member.mention}) by a moderator.",
            config.embed_info_color
        )

        warning_embed.add_field(name="Warning ID", value=warning_id, inline=True)
        warning_embed.add_field(name="Member in Question", value=f"{member.name} ({member.mention})", inline=False)
        warning_embed.add_field(name="Warning Issued By", value=f"{moderator.name} ({moderator.mention})", inline=True)
        warning_embed.add_field(name="Reason for Warning", value=warning["reason"], inline=False)

        return await ctx.reply(embed=warning_embed)

    warnings_details = command_details["warnings"]

    @commands.command(name="warnings",
                      aliases=warnings_details["aliases"],
                      usage=warnings_details["usage"],
                      description=warnings_details["description"],
                      signature=warnings_details["signature"])
    @commands.has_any_role(*warnings_details["required_roles"])
    @commands.cooldown(warnings_details["cooldown_rate"], warnings_details["cooldown_per"])
    async def warnings(self, ctx, member: discord.Member):
        warning_collection = self.client.get_database_collection("warnings")

        if warning_collection.find({"member": member.id}).count() == 0:
            error_embed = self.client.create_embed(
                "No Warnings Found",
                "This member has no warnings on their profile.",
                config.embed_error_color
            )

            return await ctx.reply(embed=error_embed)

        warnings = warning_collection.find({"member": member.id})
        page_index = 0

        warnings_embed = self.client.create_embed(
            "Loading Data",
            "Currently fetching data from our database...",
            config.embed_info_color
        )

        warnings_message = await ctx.reply(embed=warnings_embed)

        await warnings_message.add_reaction("⏮")
        await warnings_message.add_reaction("⬅")
        await warnings_message.add_reaction("🛑")
        await warnings_message.add_reaction("➡")
        await warnings_message.add_reaction("⏭")

        while True:
            warning = warnings[page_index]
            moderator = await self.client.fetch_member(warning["moderator"])

            warning_embed = self.client.create_embed(
                "Warning Issued",
                f"A warning was issued to {member.name} ({member.mention}) by a moderator.",
                config.embed_info_color
            )

            warning_embed.add_field(name="Warning ID", value=warning["_id"], inline=True)
            warning_embed.add_field(name="Member in Question", value=f"{member.name} ({member.mention})", inline=False)
            warning_embed.add_field(name="Warning Issued By", value=f"{moderator.name} ({moderator.mention})", inline=True)
            warning_embed.add_field(name="Reason for Warning", value=warning["reason"], inline=False)

            await warnings_message.edit(embed=warning_embed)
            warning_reply = await self.client.message_reaction(warnings_message, ctx.author, 30)

            if warning_reply is None:
                return

            async def invalid_response():
                invalid_response_embed = self.client.create_embed("Invalid Response",
                                                                  "The response that you provided to the question was not acceptable.",
                                                                  config.embed_error_color)

                await warnings_message.edit(embed=invalid_response_embed)

            if warning_reply not in ["⏮", "⬅", "🛑", "➡", "⏭"]:
                return await invalid_response()

            await warnings_message.remove_reaction(warning_reply, ctx.author)

            if warning_reply == "⏮":
                page_index = 0
            elif warning_reply == "⬅":
                page_index -= 1
            elif warning_reply == "🛑":
                await warnings_message.remove_reaction("⏮", ctx.guild.me)
                await warnings_message.remove_reaction("⬅", ctx.guild.me)
                await warnings_message.remove_reaction("🛑", ctx.guild.me)
                await warnings_message.remove_reaction("➡", ctx.guild.me)
                await warnings_message.remove_reaction("⏭", ctx.guild.me)
                return
            elif warning_reply == "➡":
                page_index += 1
            elif warning_reply == "⏭":
                page_index = warnings.count() - 1

            if page_index == -1:
                page_index = warnings.count() - 1

            if page_index == warnings.count():
                page_index = 0

async def setup(client):
    await client.add_cog(Moderation(client), guilds=[discord.Object(id=503560012581568514)])
