import discord_module as discord

import discord
from discord.ext import commands, tasks
from json import load
from os import system
from requests import get

import config

class Guild(commands.Cog):
    with open("command_details.json", "r") as json_file:
        command_details = load(json_file)

    def __init__(self, client):
        self.client = client
        self.guild_members.start()

    @tasks.loop(minutes=5)
    async def guild_members(self):
        guild = await self.client.fetch_guild(503560012581568514)
        guild_role = guild.get_role(config.role_ids["guild"])
        user_collection = self.client.get_database_collection("users")

        async def remove_role(member):
            await member.remove_roles(guild_role, reason="Not in OUT Guild")

        for member in guild.members:
            if guild_role in member.roles:
                await self.client.database_user_preload(member.id)
                user_profile = user_collection.find_one({"_id": member.id})

                if user_profile["uuid"] is None:
                    await remove_role(member)
                    continue

                hypixel_url = f"https://api.hypixel.net/guild"
                hypixel_parameters = {"key": self.client.hypixel_key, "player": user_profile["uuid"]}
                hypixel_data = get(hypixel_url, params=hypixel_parameters).json()

                if hypixel_data["guild"] is None or hypixel_data["guild"]["name"] != "OUT":
                    await remove_role(member)
                    continue

    guildmember_details = command_details["guildmember"]

    @commands.command(
        name="guildmember",
        aliases=guildmember_details["aliases"],
        usage=guildmember_details["usage"],
        description=guildmember_details["description"],
        signature=guildmember_details["signature"])
    @commands.has_any_role(*guildmember_details["required_roles"])
    @commands.cooldown(guildmember_details["cooldown_rate"], guildmember_details["cooldown_per"])
    async def guildmember(self, ctx):
        await self.client.database_user_preload(ctx.author.id)
        user_collection = self.client.get_database_collection("users")
        user_profile = user_collection.find_one({"_id": ctx.author.id})

        if user_profile["uuid"] is None:
            uuid_embed = self.client.create_embed(
                "Invalid UUID Link",
                "You have not linked your account through Hypixel.",
                config.embed_error_color
            )

            return await ctx.reply(embed=uuid_embed)

        hypixel_url = f"https://api.hypixel.net/guild"
        hypixel_parameters = {"key": self.client.hypixel_key, "player": user_profile["uuid"]}
        hypixel_data = get(hypixel_url, params=hypixel_parameters).json()

        if hypixel_data["guild"] is None or hypixel_data["guild"]["name"] != "OUT":
            validate_embed = self.client.create_embed(
                "Unable to Validate",
                "You are not a member of the Hypixel OUT Guild.",
                config.embed_error_color
            )

            return await ctx.reply(embed=validate_embed)

        guild_role = ctx.guild.get_role(config.role_ids["guild"])
        await ctx.author.add_roles(guild_role)

        guild_embed = self.client.create_embed(
            "Welcome to The OUT Guild",
            "We hope that you enjoy your stay.",
            config.embed_success_color
        )

        return await ctx.reply(embed=guild_embed)

    inactive_details = command_details["inactive"]

    @commands.command(
        name="inactive",
        aliases=inactive_details["aliases"],
        usage=inactive_details["usage"],
        description=inactive_details["description"],
        signature=inactive_details["signature"])
    @commands.has_any_role(*inactive_details["required_roles"])
    @commands.cooldown(inactive_details["cooldown_rate"], inactive_details["cooldown_per"])
    async def inactive(self, ctx, *, reason="No Reason Given"):
        inactive_role = ctx.guild.get_role(config.role_ids["inactive"])

        if inactive_role not in ctx.author.roles:
            await ctx.author.add_roles(inactive_role, reason=reason)

            inactive_embed = self.client.create_embed(
                "Enjoy Your Break!",
                "Your leave has been recorded.",
                config.embed_success_color
            )

            return await ctx.reply(embed=inactive_embed)

        await ctx.author.remove_roles(inactive_role)

        inactive_embed = self.client.create_embed(
            "Welcome Back!",
            "Your return has been recorded.",
            config.embed_success_color
        )

        return await ctx.reply(embed=inactive_embed)

    admin_inactive_details = command_details["admin:inactive"]

    @commands.command(
        name="admin:inactive",
        aliases=admin_inactive_details["aliases"],
        usage=admin_inactive_details["usage"],
        description=admin_inactive_details["description"],
        signature=admin_inactive_details["signature"])
    @commands.has_any_role(*admin_inactive_details["required_roles"])
    @commands.cooldown(admin_inactive_details["cooldown_rate"], admin_inactive_details["cooldown_per"])
    async def admin_inactive(self, ctx, member: discord.Member, reason="No Reason Given"):
        inactive_role = ctx.guild.get_role(config.role_ids["inactive"])

        if inactive_role not in member.roles:
            await member.add_roles(inactive_role, reason=reason)

            inactive_embed = self.client.create_embed(
                "Enjoy The Break!",
                "The leave has been recorded.",
                config.embed_success_color
            )

            return await ctx.reply(embed=inactive_embed)

        await member.remove_roles(inactive_role)

        inactive_embed = self.client.create_embed(
            "Welcome Back!",
            "The return has been recorded.",
            config.embed_success_color
        )

        return await ctx.reply(embed=inactive_embed)

    restart_outbot_details = command_details["restartOUTBOT"]

    @commands.command(
        name="restartOUTBOT",
        aliases=restart_outbot_details["aliases"],
        usage=restart_outbot_details["usage"],
        description=restart_outbot_details["description"],
        signature=restart_outbot_details["signature"])
    @commands.has_any_role(*restart_outbot_details["required_roles"])
    @commands.cooldown(restart_outbot_details["cooldown_rate"], restart_outbot_details["cooldown_per"])
    async def restartOUTBOT(self, ctx):
        system("pm2 restart OUTBOT")
        await ctx.send("**Restarted OUTBOT**")

async def setup(client):
    await client.add_cog(Guild(client), guilds=[discord.Object(id=503560012581568514)])
