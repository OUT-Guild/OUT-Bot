import discord_module as discord

from ast import literal_eval
from base64 import b64decode
import discord
from discord import utils
from discord.ext import commands, tasks
from io import BytesIO
from json import load
from numpy import array, uint8
from PIL import Image
from random import randint
from requests import get
from time import time

import config

class Coins(commands.Cog):
    with open("command_details.json", "r") as json_file:
        command_details = load(json_file)

    def __init__(self, client):
        self.client = client
        self.messages = {}
        self.converter = commands.MemberConverter()

        self.emotes.start()
        self.booster_colors.start()

    @tasks.loop(minutes=5)
    async def emotes(self):
        guild = await self.client.fetch_guild(503560012581568514)
        booster_role = guild.get_role(config.role_ids["guild"])
        staff_role = guild.get_role(config.role_ids["staff"])
        override_role = guild.get_role(config.role_ids["override"])

        user_collection = self.client.get_database_collection("users")
        for user in user_collection.find({"emote": {"$ne": None}}):
            member = await guild.fetch_member(user["_id"])

            if booster_role not in member.roles and staff_role not in member.roles and override_role not in member.roles:
                emote = await guild.fetch_emoji(user["emote"])
                await emote.delete()

                user_collection.update_one({"_id": member.id}, {"$set": {"emote": None}})

    @tasks.loop(minutes=5)
    async def booster_colors(self):
        guild = await self.client.fetch_guild(503560012581568514)
        booster_role = guild.get_role(config.role_ids["guild"])
        booster_color_roles = [guild.get_role(role_id) for role_id in config.role_ids["booster_colors"]]

        async def remove_roles(member):
            await member.remove_roles(*booster_color_roles, reason="Not a Nitro Booster")

        for member in guild.members:
            if booster_role not in member.roles:
                await remove_roles(member)
                continue

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            if message.channel.category_id != config.category_ids["bots"]:
                current_time = time()
                time_requirement = current_time - 60

                if self.messages.get(message.author.id, 0) <= time_requirement:
                    if utils.get(message.guild.roles, id=config.role_ids["booster"]) in message.author.roles:
                        randomizer = config.booster_randomizer
                    elif utils.get(message.guild.roles, id=config.role_ids["guild"]) in message.author.roles:
                        randomizer = config.guild_randomizer
                    elif utils.get(message.guild.roles, id=config.role_ids["member"]) in message.author.roles:
                        randomizer = config.member_randomizer
                    else:
                        randomizer = (0, 0)

                    await self.client.database_user_preload(message.author.id)
                    user_collection = self.client.get_database_collection("users")
                    user_collection.update_one({"_id": message.author.id},
                                               {"$inc": {"coins": randint(randomizer[0], randomizer[1])}})
                    self.messages[message.author.id] = current_time

    profile_details = command_details["profile"]

    @commands.command(name="profile",
                      aliases=profile_details["aliases"],
                      usage=profile_details["usage"],
                      description=profile_details["description"],
                      signature=profile_details["signature"])
    @commands.has_any_role(*profile_details["required_roles"])
    @commands.cooldown(profile_details["cooldown_rate"], profile_details["cooldown_per"])
    async def profile(self, ctx, member: discord.Member = None):
        if member is None: member = ctx.author
        await self.client.database_user_preload(member.id)

        user_collection = self.client.get_database_collection("users")
        user_profile = user_collection.find_one({"_id": member.id})

        profile_embed = self.client.create_embed("Member Profile",
                                                 f"{member.name} ({member.mention})'s OUT Account Details",
                                                 config.embed_info_color)

        for role in member.roles[::-1]:
            if role.hoist:
                member_role = role
                break

        if user_profile["supporting"] is not None:
            supporting = f"<@!{user_profile['supporting']}>"
        else:
            supporting = "nobody :("

        badges = ""

        badgeRank = 0
        for badge in user_profile["badges"]:
            if "ranktier" in badge:
                badgeRank += 1
            else:
                badges += f"<:{badge}:{config.badge_ids[badge]}> "
        if badgeRank > 0:
            badges += f"<:rank:{config.badge_ids[f'ranktier_{badgeRank}']}> "

        if badges != "":
            badges = badges[:-1]
        else:
            badges = "You Do Not Have Any Badges..."

        profile_embed.add_field(name="Server Role", value=member_role.mention, inline=True)
        profile_embed.add_field(name="OUT Coins", value=f"{user_profile['outcoins']} <:outcoin:{config.emoji_ids['coin']}>", inline=True)
        profile_embed.add_field(name="Supporting", value=supporting, inline=True)
        profile_embed.add_field(name="Badges", value=badges, inline=False)

        return await ctx.send(embed=profile_embed)

    shop_details = command_details["shop"]

    @commands.command(name="shop",
                      aliases=shop_details["aliases"],
                      usage=shop_details["usage"],
                      description=shop_details["description"],
                      signature=shop_details["signature"])
    @commands.has_any_role(*shop_details["required_roles"])
    @commands.cooldown(shop_details["cooldown_rate"], shop_details["cooldown_per"])
    async def shop(self, ctx, category=None):
        if category is None:
            category_embed = self.client.create_embed("OUT Shop Categories", "A list of every shop category that you can buy from!", config.embed_info_color)

            for shop_category in config.shop_categories:
                formal_category = config.formal_shop_categories[shop_category]
                category_embed.add_field(name=formal_category, value=f"`!shop {shop_category}`", inline=False)

            category_embed.set_footer(text="No Refunds!")
            return await ctx.reply(embed=category_embed)

        category = category.lower()
        if category not in config.shop_categories:
            category_embed = self.client.create_embed("Invalid Shop Category", "There is no shop category by that name.", config.embed_error_color)
            return await ctx.reply(embed=category_embed)

        await self.client.database_user_preload(ctx.author.id)
        user_collection = self.client.get_database_collection("users")
        user_profile = user_collection.find_one({"_id": ctx.author.id})

        shop_embed = self.client.create_embed("OUT Shop", "Loading Shop Items...", config.embed_info_color)
        shop_message = await ctx.reply(embed=shop_embed)

        await shop_message.add_reaction("⬅")
        await shop_message.add_reaction(f"<:outcoin:{config.emoji_ids['coin']}>")
        await shop_message.add_reaction("➡")

        shop_items = config.category_items[category]
        item_index = 0

        index_bounds = (0, len(shop_items) - 1)

        while True:
            shop_item = shop_items[item_index]
            item_type = shop_item["type"]

            if item_type == "role":
                item_preview = f"<@&{shop_item['role_id']}>"
            elif item_type == "badge":
                item_preview = f"<:{shop_item['badge_id']}:{config.badge_ids[shop_item['badge_id']]}>"
            elif item_type == "rank_badge_transaction":
                item_preview = f"<:rank:{config.emoji_ids['rank']}>"
            elif category == "hypixel":
                item_preview = f"<:hypixelemoji:{config.emoji_ids['hypixel']}>"
            else:
                item_preview = f"<:outemoji:{config.emoji_ids['out']}>"

            item_embed = self.client.create_embed("OUT Shop", shop_item["description"], config.embed_info_color)
            item_embed.add_field(name=shop_item["name"], value=f"Price: {shop_item['price']} <:outcoin:{config.emoji_ids['coin']}>\n{item_preview}", inline=True)

            if shop_item["type"] == "rank_badge_transaction":
                rank_tier = 1

                for badge in user_profile["badges"]:
                    if shop_item["badge_identifier"] in badge:
                        rank_tier += int(badge[-1])

                if rank_tier > 4:
                    rank_tier = 4

                item_embed.set_footer(text=f"Purchasing Tier {rank_tier}/{shop_item['badge_tiers']}")

            await shop_message.edit(embed=item_embed)
            shop_reply = await self.client.message_reaction(shop_message, ctx.author, 30)

            if shop_reply is None:
                return

            async def invalid_response():
                invalid_response_embed = self.client.create_embed("Invalid Response",
                                                                  "The response that you provided to the question was not acceptable.",
                                                                  config.embed_error_color)

                await shop_message.edit(embed=invalid_response_embed)

            if shop_reply not in ["⬅", f"<:outcoin:{config.emoji_ids['coin']}>", "➡"]:
                return await invalid_response()

            await shop_message.remove_reaction(shop_reply, ctx.author)
            if shop_reply == "⬅":
                item_index -= 1

                if item_index < index_bounds[0]:
                    item_index = index_bounds[1]
            elif shop_reply == "➡":
                item_index += 1

                if item_index > index_bounds[1]:
                    item_index = index_bounds[0]
            else:  # Purchasing Item
                if user_profile["outcoins"] < shop_item["price"]:
                    price_embed = self.client.create_embed("Invalid Item Purchase", "You are unable to purchase this item as your lack sufficient funds.", config.embed_error_color)
                    return await shop_message.edit(embed=price_embed)

                user_collection.update_one({"_id": ctx.author.id}, {"$inc": {"outcoins": -1 * shop_item["price"]}})

                if user_profile["supporting"] is not None:
                    user_collection.update_one({"_id": user_profile["supporting"]}, {"$inc": {"outcoins": shop_item["price"] * config.support_rate}})

                if item_type == "role":
                    role_id = shop_item["role_id"]

                    for role in ctx.author.roles:
                        if role.id == role_id:
                            role_embed = self.client.create_embed("Invalid Item Purchase", "You are unable to purchase this item as you already own it.", config.embed_error_color)
                            return await shop_message.edit(embed=role_embed)

                    item_purchased = ctx.guild.get_role(role_id)
                    await ctx.author.add_roles(item_purchased, reason="Purchased from OUT Shop")
                elif item_type == "badge":
                    badge_id = shop_item["badge_id"]

                    if badge_id in user_profile["badges"]:
                        bade_embed = self.client.create_embed("Invalid Item Purchase", "You are unable to purchase this item as you already own it.", config.embed_error_color)
                        return await shop_message.edit(embed=bade_embed)

                    user_collection.update_one({"_id": ctx.author.id}, {"$push": {"badges": badge_id}})
                elif item_type == "rank_badge_transaction":
                    badge_id = f"{shop_item['badge_identifier']}_{rank_tier}"

                    if badge_id in user_profile["badges"]:
                        bade_embed = self.client.create_embed("Invalid Item Purchase", "You are unable to purchase this item as you already own it.", config.embed_error_color)
                        return await shop_message.edit(embed=bade_embed)

                    if rank_tier > 1:
                        tier_id = f"{shop_item['badge_identifier']}_{rank_tier - 1}"
                        user_collection.update_one({"_id": ctx.author.id}, {"$pull": {"badges": tier_id}})

                    user_collection.update_one({"_id": ctx.author.id}, {"$push": {"badges": badge_id}})

                    if rank_tier == 1:
                        suffix = "st"
                    elif rank_tier == 2:
                        suffix = "nd"
                    elif rank_tier == 3:
                        suffix = "rd"
                    else:
                        suffix = "th"

                    transaction_embed = self.client.create_embed("Transaction Made", shop_item["transaction"].format(member=ctx.author, tier=rank_tier, suffix=suffix), config.embed_info_color)
                    transaction_embed.add_field(name="OUT Coins Spent", value=f"{shop_item['price']} <:outcoin:{config.emoji_ids['coin']}>", inline=True)
                    transaction_embed.add_field(name="Staff Member Responsible", value=f"<@!{shop_item['staff_id']}>", inline=True)
                    transaction_embed.set_footer(text="Delete This Once Completed!")

                    transaction_channel = self.client.get_channel(config.channel_ids["transaction_logs"])
                    await transaction_channel.send(embed=transaction_embed)
                    
                    notification_message = await transaction_channel.send(f"<@!{shop_item['staff_id']}>")
                    await notification_message.delete()
                elif item_type == "transaction":
                    transaction_embed = self.client.create_embed("Transaction Made", shop_item["transaction"].format(member=ctx.author), config.embed_info_color)
                    transaction_embed.add_field(name="OUT Coins Spent", value=f"{shop_item['price']} <:outcoin:{config.emoji_ids['coin']}>", inline=True)
                    transaction_embed.add_field(name="Staff Member Responsible", value=f"<@!{shop_item['staff_id']}>", inline=True)
                    transaction_embed.set_footer(text="Delete This Once Completed!")

                    transaction_channel = self.client.get_channel(config.channel_ids["transaction_logs"])
                    await transaction_channel.send(embed=transaction_embed)

                    notification_message = await transaction_channel.send(f"<@!{shop_item['staff_id']}>")
                    await notification_message.delete()
                    
                purchased_embed = self.client.create_embed("Item Purchased", "Your item has been successfully purchased, please allow us time to process your transaction.", config.embed_success_color)
                purchased_embed.add_field(name="Item Purchased", value=shop_item["name"], inline=True)
                purchased_embed.add_field(name="OUT Coins Spent", value=f"{shop_item['price']} <:outcoin:{config.emoji_ids['coin']}>", inline=True)

                if user_profile["supporting"] is not None:
                    purchased_embed.set_footer(text=f"Supported: <@!{user_profile['supporting']}>")

                return await shop_message.edit(embed=purchased_embed)

    support_details = command_details["support"]

    @commands.command(name="support",
                      aliases=support_details["aliases"],
                      usage=support_details["usage"],
                      description=support_details["description"],
                      signature=support_details["signature"])
    @commands.has_any_role(*support_details["required_roles"])
    @commands.cooldown(support_details["cooldown_rate"], support_details["cooldown_per"])
    async def support(self, ctx, member: discord.Member):
        await self.client.database_user_preload(ctx.author.id)
        await self.client.database_user_preload(member.id)
        user_collection = self.client.get_database_collection("users")

        if member.id == ctx.author.id:
            greedy_embed = self.client.create_embed("Greedy Loser", "That low, huh?", config.embed_error_color)
            return await ctx.reply(embed=greedy_embed)

        user_collection.update_one({"_id": ctx.author.id}, {"$set": {"supporting": member.id}})
        supporting_embed = self.client.create_embed("Now Supporting", f"You are now supporting {member.mention}.", config.embed_success_color)
        return await ctx.reply(embed=supporting_embed)

    emote_details = command_details["emote"]

    @commands.command(name="emote",
                      aliases=emote_details["aliases"],
                      usage=emote_details["usage"],
                      description=emote_details["description"],
                      signature=emote_details["signature"])
    @commands.has_any_role(*emote_details["required_roles"])
    @commands.cooldown(emote_details["cooldown_rate"], emote_details["cooldown_per"])
    async def emote(self, ctx):
        await self.client.database_user_preload(ctx.author.id)
        user_collection = self.client.get_database_collection("users")
        user_profile = user_collection.find_one({"_id": ctx.author.id})
        uuid = user_profile["uuid"]

        if uuid is None:
            verification_embed = self.client.create_embed("You have not verified!", "I am unable to create an emote until you have verified.", config.embed_error_color)
            return await ctx.reply(embed=verification_embed)

        mojangPlayerObject = get(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid.replace('-', '')}").json()
        decodedTextures = b64decode(mojangPlayerObject["properties"][0]["value"])
        decodedDictionary = literal_eval(decodedTextures.decode("UTF-8"))
        rawSkinBytes = get(decodedDictionary["textures"]["SKIN"]["url"])
        decodedSkin = BytesIO(rawSkinBytes.content)
        background, foreground = Image.open(decodedSkin), Image.open(decodedSkin)
        background = background.crop(box=(8, 8, 16, 16))
        foreground = foreground.crop(box=(40, 8, 48, 16))
        background.paste(foreground, (0, 0), foreground)
        backgroundData = list(background.getdata())
        smallPixels = [backgroundData[:8], backgroundData[8:16], backgroundData[16:24], backgroundData[24:32],
                       backgroundData[32:40], backgroundData[40:48], backgroundData[48:56], backgroundData[56:]]
        pixels = []

        for smallRow in smallPixels:
            row = []

            for smallPixel in smallRow:
                r = smallPixel[0]
                g = smallPixel[1]
                b = smallPixel[2]

                for _ in range(32):
                    row.append((r, g, b))

            for _ in range(32):
                pixels.append(row)

        largePixels = array(pixels, dtype=uint8)
        largeImage = Image.fromarray(largePixels)

        with BytesIO() as image_binary:
            largeImage.save(image_binary, "PNG")
            largeImage.seek(0)

            if user_profile["emote"] is None:
                emote = await ctx.guild.create_custom_emoji(name=mojangPlayerObject["name"].lower(), image=image_binary.getvalue())
                user_collection.update_one({"_id": ctx.author.id}, {"$set": {"emote": emote.id}})
            else:
                emote_id = user_profile["emote"]
                emote = await ctx.guild.fetch_emoji(emote_id)
                await emote.delete()

                emote = await ctx.guild.create_custom_emoji(name=mojangPlayerObject["name"].lower(), image=image_binary.getvalue())
                user_collection.update_one({"_id": ctx.author.id}, {"$set": {"emote": emote.id}})

        await ctx.message.add_reaction(emote)

    giftcoins_details = command_details["giftcoins"]

    @commands.command(name="giftcoins",
                      aliases=giftcoins_details["aliases"],
                      usage=giftcoins_details["usage"],
                      description=giftcoins_details["description"],
                      signature=giftcoins_details["signature"])
    @commands.has_any_role(*giftcoins_details["required_roles"])
    @commands.cooldown(giftcoins_details["cooldown_rate"], giftcoins_details["cooldown_per"])
    async def giftcoins(self, ctx, member: discord.Member, amount: int):
        await self.client.database_user_preload(ctx.author.id)
        await self.client.database_user_preload(member.id)
        user_collection = self.client.get_database_collection("users")
        user_profile = user_collection.find_one({"_id": ctx.author.id})

        if user_profile["outcoins"] < amount:
            coins_embed = self.client.create_embed("Invalid Gift", "You are unable to gift these OUT Coins due to insufficient funds.", config.embed_error_color)
            return await ctx.reply(embed=coins_embed)

        if member.id == ctx.author.id or amount < 1:
            greedy_embed = self.client.create_embed("Greedy Loser", "That low, huh?", config.embed_error_color)
            return await ctx.reply(embed=greedy_embed)

        user_collection.update_one({"_id": ctx.author.id}, {"$inc": {"outcoins": -1 * amount}})
        user_collection.update_one({"_id": member.id}, {"$inc": {"outcoins": amount}})

        gift_embed = self.client.create_embed("OUT Coins Gifted", "Your gift has been successfully transferred.", config.embed_success_color)
        gift_embed.add_field(name="From", value=ctx.author.mention, inline=True)
        gift_embed.add_field(name="To", value=member.mention, inline=True)
        gift_embed.add_field(name="OUT Coins Gifted", value=f"{amount} <:outcoin:{config.emoji_ids['coin']}>", inline=True)

        return await ctx.reply(embed=gift_embed)

    outcoins = command_details["outcoins"]

    @commands.command(name="outcoins",
                      aliases=outcoins["aliases"],
                      usage=outcoins["usage"],
                      description=outcoins["description"],
                      signature=outcoins["signature"])
    @commands.has_any_role(*outcoins["required_roles"])
    @commands.cooldown(outcoins["cooldown_rate"], outcoins["cooldown_per"])
    async def outcoins(self, ctx, argument, amount: int, *args: discord.Member):
        argument = argument.lower()
        user_collection = self.client.get_database_collection("users")
        member_ids = list(map(lambda member: member.id, args))
        member_identifications = list(map(lambda member: f"{member.name} ({member.mention})", args))

        if argument in ["add", "inc"]:
            for member in args:
                await self.client.database_user_preload(member.id)

            user_collection.update_many({"_id": {"$in": member_ids}}, {"$inc": {"outcoins": amount}})
            coins_embed = self.client.create_embed("OUT Coins Added", "The respective member(s) have received their OUT Coins.", config.embed_success_color)
            await ctx.reply(embed=coins_embed)

            log_embed = self.client.create_embed("OUT Coins Added", "OUT Coins have been distributed by a moderator.", config.embed_info_color)
            log_embed.add_field(name="Member(s)", value=", ".join(member_identifications), inline=True)
            log_embed.add_field(name="Moderator", value=f"{ctx.author.name} ({ctx.author.mention})")
            log_embed.add_field(name="Amount", value=f"{amount} <:outcoin:{config.emoji_ids['coin']}>", inline=False)

            log_channel = self.client.get_channel(config.channel_ids["miscellaneous_logs"])
            return await log_channel.send(embed=log_embed)
        elif argument in ["subtract", "sub"]:
            for member in args:
                await self.client.database_user_preload(member.id)

            user_collection.update_many({"_id": {"$in": member_ids}}, {"$inc": {"outcoins": -1 * amount}})
            coins_embed = self.client.create_embed("OUT Coins Removed", "The respective member(s) have been removed of their OUT Coins.", config.embed_success_color)
            await ctx.reply(embed=coins_embed)

            log_embed = self.client.create_embed("OUT Coins Removed", "OUT Coins have been taken by a moderator.", config.embed_info_color)
            log_embed.add_field(name="Member(s)", value=", ".join(member_identifications), inline=True)
            log_embed.add_field(name="Moderator", value=f"{ctx.author.name} ({ctx.author.mention})")
            log_embed.add_field(name="Amount", value=f"{amount} <:outcoin:{config.emoji_ids['coin']}>", inline=False)

            log_channel = self.client.get_channel(config.channel_ids["miscellaneous_logs"])
            return await log_channel.send(embed=log_embed)
        else:
            argument_embed = self.client.create_embed("Invalid Argument", "The argument that you provided was not acceptable.", config.embed_error_color)
            return await ctx.reply(embed=argument_embed)

    outcoins_top = command_details["outcoins_top"]

    @commands.command(name="outcoinstop",
                      aliases=outcoins_top["aliases"],
                      usage=outcoins_top["usage"],
                      description=outcoins_top["description"],
                      signature=outcoins_top["signature"])
    @commands.has_any_role(*outcoins_top["required_roles"])
    @commands.cooldown(outcoins_top["cooldown_rate"], outcoins_top["cooldown_per"])
    async def outcoins_top(self, ctx, places: int=10):
        class LeaderBoardPosition:
            def __init__(self, id, coins):
                self.id = id
                self.coins = coins

        leaderboard = []
        user_collection = self.client.get_database_collection("users")

        for user in user_collection.find():
            leaderboard.append(LeaderBoardPosition(user["_id"], user["outcoins"]))

        top = sorted(leaderboard, key=lambda x: x.coins, reverse=True)
        leaderboard_embed = self.client.create_embed("OUT Coin Leaderboard", f"The top {places} wealthiest people in all of OUT!", config.embed_info_color)

        for i in range(1, places + 1, 1):
            try:
                value_one = top[i - 1].id
                value_two = top[i - 1].coins

                leaderboard_embed.add_field(name=f"{i}. <:outcoin:{config.emoji_ids['coin']}> {value_two}", value=f"<@!{value_one}>", inline=False)
            except IndexError:
                leaderboard_embed.add_field(name=f"**<< {i} >>**", value="N/A | NaN", inline=False)

        return await ctx.reply(embed=leaderboard_embed)

async def setup(client):
    await client.add_cog(Coins(client), guilds=[discord.Object(id=503560012581568514)])
