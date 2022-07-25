import discord_module as discord

import discord
from discord.ext import commands
from json import load
from requests import get

import config

class Welcomes(commands.Cog):
    with open("command_details.json", "r") as json_file:
        command_details = load(json_file)

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.bot:
            await self.client.database_user_preload(member.id)

            channel = member.guild.get_channel(config.channel_ids["welcomes"])
            await channel.send(f":boom::boom:Welcome to OUT! {member.mention}឵, you're member number {member.guild.member_count}, Remember to read the rules. Have fun!:boom::boom:")

    link_details = command_details["link"]

    @commands.command(name="link",
                      aliases=link_details["aliases"],
                      usage=link_details["usage"],
                      description=link_details["description"],
                      signature=link_details["signature"])
    @commands.has_any_role(*link_details["required_roles"])
    @commands.cooldown(link_details["cooldown_rate"], link_details["cooldown_per"])
    async def link(self, ctx, username):
        await self.client.database_user_preload(ctx.author.id)
        user_collection = self.client.get_database_collection("users")

        mojang_url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
        mojang_data = get(mojang_url).json()
        uuid = mojang_data["id"]

        if user_collection.find({"uuid": uuid}).count() == 0:
            hypixel_url = f"https://api.hypixel.net/player"
            hypixel_parameters = {"key": self.client.hypixel_key, "uuid": uuid}
            hypixel_data = get(hypixel_url, params=hypixel_parameters).json()

            if hypixel_data["player"]["socialMedia"]["links"]["DISCORD"].lower() != str(ctx.author).lower():
                invalid_embed = self.client.create_embed("Invalid Discord Tag",
                                                         f"That account's Discord is not set to {str(ctx.author)}.",
                                                         config.embed_error_color)

                return await ctx.reply(embed=invalid_embed)

            if hypixel_data["player"]["networkExp"] < 1305000:
                insufficient_embed = self.client.create_embed("Insufficient Network Level",
                                                              "That account does not have a network level of 30 or higher.",
                                                              config.embed_error_color)

                return await ctx.reply(embed=insufficient_embed)

            user_collection.update_one({"_id": ctx.author.id}, {"$set": {"uuid": uuid}})
            role = discord.utils.get(ctx.guild.roles, id=707624818090049627)
            await ctx.author.add_roles(role)
        else:
            user = user_collection.find_one({"uuid": uuid})

            if user["_id"] != ctx.author.id:
                claimed_embed = self.client.create_embed("Account Already Claimed",
                                                         "That account has already been linked to an OUT Profile.",
                                                         config.embed_error_color)

                return await ctx.reply(embed=claimed_embed)

            role = discord.utils.get(ctx.guild.roles, id=707624818090049627)
            await ctx.author.add_roles(role)

    admin_link_details = command_details["admin:link"]

    @commands.command(name="admin:link",
                      aliases=admin_link_details["aliases"],
                      usage=admin_link_details["usage"],
                      description=admin_link_details["description"],
                      signature=admin_link_details["signature"])
    @commands.has_any_role(*admin_link_details["required_roles"])
    @commands.cooldown(admin_link_details["cooldown_rate"], admin_link_details["cooldown_per"])
    async def admin_link(self, ctx, member: discord.Member, username):
        await self.client.database_user_preload(member.id)
        user_collection = self.client.get_database_collection("users")

        mojang_url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
        mojang_data = get(mojang_url).json()
        uuid = mojang_data["id"]

        if user_collection.find({"uuid": uuid}).count() == 0:
            hypixel_url = f"https://api.hypixel.net/player"
            hypixel_parameters = {"key": self.client.hypixel_key, "uuid": uuid}
            hypixel_data = get(hypixel_url, params=hypixel_parameters).json()

            if hypixel_data["player"]["socialMedia"]["links"]["DISCORD"].lower() != str(member).lower():
                invalid_embed = self.client.create_embed("Invalid Discord Tag",
                                                         f"That account's Discord is not set to {str(member)}.",
                                                         config.embed_error_color)

                return await ctx.reply(embed=invalid_embed)

            if hypixel_data["player"]["networkExp"] < 1305000:
                insufficient_embed = self.client.create_embed("Insufficient Network Level",
                                                              "That account does not have a network level of 30 or higher.",
                                                              config.embed_error_color)

                return await ctx.reply(embed=insufficient_embed)

            user_collection.update_one({"_id": member.id}, {"$set": {"uuid": uuid}})
            role = discord.utils.get(ctx.guild.roles, id=707624818090049627)
            await member.add_roles(role)
        else:
            user = user_collection.find_one({"uuid": uuid})

            if user["_id"] != member.id:
                claimed_embed = self.client.create_embed("Account Already Claimed",
                                                         "That account has already been linked to an OUT Profile.",
                                                         config.embed_error_color)

                return await ctx.reply(embed=claimed_embed)

            role = discord.utils.get(ctx.guild.roles, id=707624818090049627)
            await member.add_roles(role)

async def setup(client):
    await client.add_cog(Welcomes(client), guilds=[discord.Object(id=503560012581568514)])
