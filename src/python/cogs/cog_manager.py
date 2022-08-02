import discord_module as discord

import discord
from discord.ext import commands
from json import load
from textwrap import indent
from time import monotonic

import config

class Cog_Manager(commands.Cog):
    with open("command_details.json", "r") as json_file:
        command_details = load(json_file)

    loaded_cogs = []

    def __init__(self, client):
        self.client = client
        self.loaded_cogs = config.cogs

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.client.user.name}#{self.client.user.discriminator}")

    cogs_details = command_details["cogs"]

    @commands.command(
        name="cogs",
        aliases=cogs_details["aliases"],
        usage=cogs_details["usage"],
        description=cogs_details["description"],
        signature=cogs_details["signature"])
    @commands.has_any_role(*cogs_details["required_roles"])
    @commands.cooldown(cogs_details["cooldown_rate"], cogs_details["cooldown_per"])
    async def cogs(self, ctx):
        embed = self.client.create_embed(
            "Cog Report",
            "The listing of the enabled and disabled cogs.",
            config.embed_info_color
        )

        booleanMapping = {True: "Enabled", False: "Disabled"}

        for cog in config.cogs:
            embed.add_field(name=config.formal_cogs[cog], value=booleanMapping[cog in self.loaded_cogs], inline=False)

        return await ctx.reply(embed=embed)

    start_cog_details = command_details["start_cog"]

    @commands.command(
        name="start_cog",
        aliases=start_cog_details["aliases"],
        usage=start_cog_details["usage"],
        description=start_cog_details["description"],
        signature=start_cog_details["signature"])
    @commands.has_any_role(*start_cog_details["required_roles"])
    @commands.cooldown(start_cog_details["cooldown_rate"], start_cog_details["cooldown_per"])
    async def start_cog(self, ctx, *cog_name):
        cog = None

        for cog_aliases in list(config.cog_aliases.values()):
            if " ".join(cog_name) in cog_aliases:
                cog = list(config.cog_aliases.keys())[list(config.cog_aliases.values()).index(cog_aliases)]

        if cog is None:
            embed = self.client.create_embed(
                "Unknown Cog",
                "The cog that you were looking for was not found in my database. If you believe this to be a false error, please contact @StarbuckBarista#3347",
                config.embed_error_color
            )

            embed.add_field(name="Command Run by", value=f"{ctx.author.mention} ({ctx.author.name})", inline=False)
            embed.add_field(name="Cog Referred", value=" ".join(cog_name), inline=True)

            return await ctx.reply(embed=embed)

        if cog in self.loaded_cogs:
            embed = self.client.create_embed(
                "Unable to Start Cog",
                "The cog that you requested has already been enabled.",
                config.embed_error_color
            )

            embed.add_field(name="Command Run by", value=f"{ctx.author.mention} ({ctx.author.name})", inline=False)
            embed.add_field(name="Cog Referred", value=cog, inline=True)

            return await ctx.reply(embed=embed)

        self.client.load_extention(f"cogs.{cog}")
        self.loaded_cogs.append(cog)

        embed = self.client.create_embed(
            "Cog Enabled",
            "The cog that you requested has been enabled.",
            config.embed_success_color
        )

        embed.add_field(name="Command Run by", value=f"{ctx.author.mention} ({ctx.author.name})", inline=False)
        embed.add_field(name="Cog Referred", value=cog, inline=True)

        return await ctx.reply(embed=embed)

    stop_cog_details = command_details["stop_cog"]

    @commands.command(
        name="stop_cog",
        aliases=stop_cog_details["aliases"],
        usage=stop_cog_details["usage"],
        description=stop_cog_details["description"],
        signature=stop_cog_details["signature"])
    @commands.has_any_role(*stop_cog_details["required_roles"])
    @commands.cooldown(stop_cog_details["cooldown_rate"], stop_cog_details["cooldown_per"])
    async def stop_cog(self, ctx, *cog_name):
        cog = None

        for cog_aliases in list(config.cog_aliases.values()):
            if " ".join(cog_name) in cog_aliases:
                cog = list(config.cog_aliases.keys())[list(config.cog_aliases.values()).index(cog_aliases)]

        if cog is None:
            embed = self.client.create_embed(
                "Unknown Cog",
                "The cog that you were looking for was not found in my database. If you believe this to be a false error, please contact @StarbuckBarista#3347",
                config.embed_error_color
            )

            embed.add_field(name="Command Run by", value=f"{ctx.author.mention} ({ctx.author.name})", inline=False)
            embed.add_field(name="Cog Referred", value=" ".join(cog_name), inline=True)

            return await ctx.reply(embed=embed)

        if cog not in self.loaded_cogs:
            embed = self.client.create_embed(
                "Unable to Stop Cog",
                "The cog that you requested has already been disabled.",
                config.embed_error_color
            )

            embed.add_field(name="Command Run by", value=f"{ctx.author.mention} ({ctx.author.name})", inline=False)
            embed.add_field(name="Cog Referred", value=cog, inline=True)

            return await ctx.reply(embed=embed)

        self.client.unload_extention(f"cogs.{cog}")
        self.loaded_cogs.remove(cog)

        embed = self.client.create_embed(
            "Cog Disabled",
            "The cog that you requested has been disabled.",
            config.embed_success_color
        )

        embed.add_field(name="Command Run by", value=f"{ctx.author.mention} ({ctx.author.name})", inline=False)
        embed.add_field(name="Cog Referred", value=cog, inline=True)

        return await ctx.reply(embed=embed)

    help_details = command_details["help"]

    @commands.command(
        name="help",
        aliases=help_details["aliases"],
        usage=help_details["usage"],
        description=help_details["description"],
        signature=help_details["signature"])
    @commands.has_any_role(*help_details["required_roles"])
    @commands.cooldown(help_details["cooldown_rate"], help_details["cooldown_per"])
    async def help(self, ctx, category=None):
        if category is None:
            category_embed = self.client.create_embed("OUT Help Categories", "A list of every help category that!", config.embed_info_color)

            for help_category in config.help_categories:
                formal_category = config.formal_help_categories[help_category]
                category_embed.add_field(name=formal_category, value=f"`!help {help_category}`", inline=False)

            return await ctx.reply(embed=category_embed)

        category = category.lower()
        if category not in config.help_categories:
            category_embed = self.client.create_embed(
                "Invalid Help Category",
                "There is no help category by that name.",
                config.embed_error_color
            )

            return await ctx.reply(embed=category_embed)

        commands = []

        for command in self.command_details:
            command_detail = self.command_details[command]

            if command_detail["cog"] == category:
                commands.append(command_detail)

        help_embed = self.client.create_embed("OUT Help Page", "Loading Commands...", config.embed_info_color)
        help_message = await ctx.reply(embed=help_embed)

        await help_message.add_reaction("⏮")
        await help_message.add_reaction("⬅")
        await help_message.add_reaction("🛑")
        await help_message.add_reaction("➡")
        await help_message.add_reaction("⏭")

        command_index = 0
        index_bounds = (0, len(commands) - 1)

        while True:
            command = commands[command_index]
            command_embed = self.client.create_embed("OUT Help Page", command["description"], config.embed_info_color)

            command_embed.add_field(
                name=command["usage"],
                value=f"Required Roles: `{', '.join(command['required_roles'])}`\nAliases: `{', '.join(command['aliases']) if len(command['aliases']) > 0 else 'None'}`",
                inline=True
            )

            command_embed.set_footer(text=f"Created by: {command['signature']}")

            await help_message.edit(embed=command_embed)
            help_reply = await self.client.message_reaction(help_message, ctx.author, 30)

            if help_reply is None:
                return

            async def invalid_response():
                await help_message.remove_reaction("⏮", ctx.guild.me)
                await help_message.remove_reaction("⬅", ctx.guild.me)
                await help_message.remove_reaction("🛑", ctx.guild.me)
                await help_message.remove_reaction("➡", ctx.guild.me)
                await help_message.remove_reaction("⏭", ctx.guild.me)

                invalid_response_embed = self.client.create_embed(
                    "Invalid Response",
                    "The response that you provided to the question was not acceptable.",
                    config.embed_error_color
                )

                await help_message.edit(embed=invalid_response_embed)

            await help_message.remove_reaction(help_reply, ctx.author)

            if help_reply not in ["⏮", "⬅", "🛑", "➡", "⏭"]:
                return await invalid_response()

            if help_reply == "⏮":
                command_index = index_bounds[0]
            elif help_reply == "⬅":
                command_index -= 1
            elif help_reply == "🛑":
                await help_message.remove_reaction("⏮", ctx.guild.me)
                await help_message.remove_reaction("⬅", ctx.guild.me)
                await help_message.remove_reaction("🛑", ctx.guild.me)
                await help_message.remove_reaction("➡", ctx.guild.me)
                await help_message.remove_reaction("⏭", ctx.guild.me)
                return
            elif help_reply == "➡":
                command_index += 1
            elif help_reply == "⏭":
                command_index = index_bounds[1]

            if command_index < index_bounds[0]:
                command_index = index_bounds[1]
            elif command_index > index_bounds[1]:
                command_index = index_bounds[0]

    ping_details = command_details["ping"]

    @commands.command(
        name="ping",
        aliases=ping_details["aliases"],
        usage=ping_details["usage"],
        description=ping_details["description"],
        signature=ping_details["signature"])
    @commands.has_any_role(*ping_details["required_roles"])
    @commands.cooldown(ping_details["cooldown_rate"], ping_details["cooldown_per"])
    async def ping(self, ctx):
        before = monotonic()
        ping_embed = self.client.create_embed("🏓 Ping!", "Processing Response...", config.embed_info_color)
        pong_message = await ctx.reply(embed=ping_embed)

        ping = round((monotonic() - before) * 1000)
        pong_embed = self.client.create_embed("🏓 Pong!", "Response Processed!", config.embed_info_color)
        pong_embed.add_field(name="Response Time", value=f"Response took {ping} ms")

        await pong_message.edit(embed=pong_embed)

    eval_details = command_details["eval"]

    @commands.command(
        name="eval",
        aliases=eval_details["aliases"],
        usage=eval_details["usage"],
        description=eval_details["description"],
        signature=eval_details["signature"])
    @commands.has_any_role(*eval_details["required_roles"])
    @commands.cooldown(eval_details["cooldown_rate"], eval_details["cooldown_per"])
    async def eval(self, ctx, *, code):
        a = {
            "self": self,
            "discord": discord,
            "ctx": ctx
        }

        exec(f"async def eval():\n{indent(code, '    ')}", a)
        await a["eval"]()

async def setup(client):
    await client.add_cog(Cog_Manager(client), guilds=[discord.Object(id=503560012581568514)])
