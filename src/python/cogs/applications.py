import discord_module as discord

import discord
from discord.errors import Forbidden
from discord.ext import commands
from json import load
from random import choice
from string import ascii_uppercase

import config

class Applications(commands.Cog):
    with open("command_details.json", "r") as json_file:
        command_details = load(json_file)

    def __init__(self, client):
        self.client = client

    apply_details = command_details["apply"]

    @commands.command(
        name="apply",
        aliases=apply_details["aliases"],
        usage=apply_details["usage"],
        description=apply_details["description"],
        signature=apply_details["signature"])
    @commands.has_any_role(*apply_details["required_roles"])
    @commands.cooldown(apply_details["cooldown_rate"], apply_details["cooldown_per"])
    async def apply(self, ctx):
        if ctx.channel.id != config.channel_ids["apply"]:
            error_embed = self.client.create_embed(
                "Incorrect Channel",
                f"This command may only be used in <#{config.channel_ids['apply']}>.",
                config.embed_error_color
            )

            return await ctx.reply(embed=error_embed)

        application_channel = await ctx.author.create_dm()
        question_responses = []

        async def dms_disabled():
            dms_embed = self.client.create_embed(
                "DMs Disabled",
                "Your DMs must be enabled in order to fill out an application.",
                config.embed_error_color
            )

            await ctx.reply(embed=dms_embed)

        async def invalid_response(message):
            invalid_response_embed = self.client.create_embed(
                "Invalid Response",
                "The response that you provided to the question was not acceptable.",
                config.embed_error_color
            )

            await message.reply(embed=invalid_response_embed)

        gamemodes_selected = []

        def get_application_embed(gamemodes_selected):
            application_embed = self.client.create_embed(
                "Welcome to the OUT Application! Which gamemodes do you have notable stats in?",
                "Press the checkmark when finished selecting all notable gamemodes.",
                config.embed_info_color
            )

            application_embed.add_field(
                name="​",
                value="🌳 - Skyblock\n🛏️ - Bedwars\n☁️ - Skywars\n⚔️ - Duels\n🏹 - Murder Mystery\n🕳️ - Pit\n🍎 - UHC\n🧨 - TNT Games\n🎮 - Arcade"
            )

            application_embed.add_field(
                name="​",
                value="🔔 - Classic Games\n🐑 - Wool Wars\n🛠️ - Build Battle\n🥕 - SpeedUHC\n🌟 - Blitz\n🪓 - Warlords\n🥊 - Smash Heroes\n🏰 - Mega Walls\n🔫 - Cops and Crims"
            )

            application_embed.add_field(
                name="Gamemodes Selected:",
                value="None" if len(gamemodes_selected) == 0 else ", ".join(gamemodes_selected),
                inline=False
            )

            return application_embed

        try:
            application_gamemodes_message = await application_channel.send(embed=get_application_embed(gamemodes_selected))
        except Forbidden:  # The user has DMs disabled
            return await dms_disabled()

        for gamemode_emoji in config.gamemode_emojis:
            await application_gamemodes_message.add_reaction(gamemode_emoji)

        while True:
            application_gamemodes_reply = await self.client.message_reaction(application_gamemodes_message, ctx.author, 60)
            if application_gamemodes_reply is None: break
            if config.gamemode_emojis[application_gamemodes_reply] == "Finished": break

            if application_gamemodes_reply not in config.gamemode_emojis:
                await application_gamemodes_message.remove_reaction(application_gamemodes_reply, ctx.author)
            else:
                gamemodes_selected.append(config.gamemode_emojis[application_gamemodes_reply])
                await application_gamemodes_message.edit(embed=get_application_embed(gamemodes_selected))

        for question in config.application_questions:
            while True:
                try:
                    application_question_message = await application_channel.send(question)
                except Forbidden:  # The user has DMs disabled
                    return await dms_disabled()

                application_question_reply = await self.client.message_response(application_question_message, ctx.author, 900)

                if len(application_question_reply.content.replace(" ", "")) == 0:  # The member replied with an image
                    image_embed = self.client.create_embed(
                        "Responded With Image",
                        "You may not answer application questions with images.",
                        config.embed_error_color
                    )

                    await application_question_reply.reply(embed=image_embed)
                elif len(application_question_reply.content) > 1024:
                    length_embed = self.client.create_embed(
                        "Responded With Long Answer",
                        "You may not exceed 1024 characters with your application responses.",
                        config.embed_error_color
                    )

                    await application_question_reply.reply(embed=length_embed)
                else:
                    question_responses.append(application_question_reply.content)
                    break

        try:
            application_confirm_message = await application_question_reply.reply("You have successfully answered all of the questions on your application. Are you certain that you would like to submit your application?")
        except Forbidden:  # The user has DMs disabled
            return await dms_disabled()

        await application_confirm_message.add_reaction("✅")
        await application_confirm_message.add_reaction("❌")

        application_confirm_reply = await self.client.message_reaction(application_confirm_message, ctx.author, 30)

        if application_confirm_reply is None:
            return

        if application_confirm_reply not in ["✅", "❌"]:
            return await invalid_response(application_confirm_message)

        if application_confirm_reply == "✅":
            question_responses[1] = question_responses[1].replace("_", r"\_")  # Prevents usernames from being subjected to markdown
            application_collection = self.client.get_database_collection("applications")

            while True:
                application_id = "".join([choice(ascii_uppercase) for _ in range(6)])

                if application_collection.count_documents({"_id": application_id}) == 0:
                    application_collection.insert_one({
                        "_id": application_id,
                        "member": ctx.author.id,
                        "gamemodes": gamemodes_selected,
                        "answers": question_responses,
                        "status": "PENDING"
                    })

                    break

            application_embed = self.client.create_embed(
                "Application Submitted",
                f"Guild application from {ctx.author.name} ({ctx.author.mention}).",
                config.embed_info_color
            )

            application_embed.add_field(
                name="Gamemodes Selected:",
                value="None" if len(gamemodes_selected) == 0 else ", ".join(gamemodes_selected),
                inline=False
            )

            for question_number, question_answer in enumerate(question_responses, 1):
                application_embed.add_field(
                    name=f"{question_number}. {config.application_questions[question_number - 1].splitlines()[1]}",
                    value=question_answer,
                    inline=False
                )

            application_embed.set_footer(text=f"Application ID: {application_id}")

            applications_channel = self.client.get_channel(config.channel_ids["applications"])
            await applications_channel.send(embed=application_embed)

            success_embed = self.client.create_embed(
                "Application Submitted",
                "Your application has been sent to our staff team for review, good luck!",
                config.embed_info_color
            )

            await application_confirm_message.reply(embed=success_embed)
        else:
            cancelled_embed = self.client.create_embed(
                "Application Cancelled",
                "Your application has been cancelled and was not submitted to our staff team. You always have the opportunity to apply again if you're interested in joining OUT.",
                config.embed_info_color
            )

            await application_confirm_message.reply(embed=cancelled_embed)

    application_details = command_details["application"]

    @commands.command(
        name="application",
        aliases=application_details["aliases"],
        usage=application_details["usage"],
        description=application_details["description"],
        signature=application_details["signature"])
    @commands.has_any_role(*application_details["required_roles"])
    @commands.cooldown(application_details["cooldown_rate"], application_details["cooldown_per"])
    async def application(self, ctx, application_id):
        application_collection = self.client.get_database_collection("applications")

        if application_collection.count_documents({"_id": application_id}) == 0:
            error_embed = self.client.create_embed(
                "Application Not Found",
                "No application with that ID was found in my database.",
                config.embed_error_color
            )

            return await ctx.reply(embed=error_embed)

        application = application_collection.find_one({"_id": application_id})
        applicant = await self.client.fetch_member(application["member"])

        application_embed = self.client.create_embed(
            f"Application #{application['_id']}",
            f"Staff application from {applicant.name} ({applicant.mention}).",
            config.embed_info_color
        )

        application_embed.add_field(
            name="Gamemodes Selected:",
            value="None" if len(application["gamemodes"]) == 0 else ", ".join(application["gamemodes"]),
            inline=False
        )

        for question_number, question_answer in enumerate(application["answers"], 1):
            application_embed.add_field(
                name=f"{question_number}. {config.application_questions[question_number - 1].splitlines()[1]}",
                value=question_answer, inline=False
            )

        return await ctx.reply(embed=application_embed)

    applications_details = command_details["applications"]

    @commands.command(
        name="applications",
        aliases=applications_details["aliases"],
        usage=applications_details["usage"],
        description=applications_details["description"],
        signature=applications_details["signature"])
    @commands.has_any_role(*applications_details["required_roles"])
    @commands.cooldown(applications_details["cooldown_rate"], applications_details["cooldown_per"])
    async def applications(self, ctx):
        applications_filter_embed = self.client.create_embed(
            "Applications Filter",
            "What filters would you like to apply to the applications database?\n:one: No Filter\n:two: Unread\n:three: Accepted\n:four: Rejected\n:five: Cancelled",
            config.embed_info_color
        )

        message = await ctx.reply(embed=applications_filter_embed)

        await message.add_reaction("1️⃣")
        await message.add_reaction("2️⃣")
        await message.add_reaction("3️⃣")
        await message.add_reaction("4️⃣")
        await message.add_reaction("5️⃣")

        applications_filter_reply = await self.client.message_reaction(message, ctx.author, 25)

        if applications_filter_reply is None:
            return

        async def invalid_response():
            invalid_response_embed = self.client.create_embed(
                "Invalid Response",
                "The response that you provided to the question was not acceptable.",
                config.embed_error_color
            )

            await message.edit(embed=invalid_response_embed)

        if applications_filter_reply not in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]:
            return await invalid_response()

        await message.remove_reaction(applications_filter_reply, ctx.author)

        await message.remove_reaction("1️⃣", self.client.user)
        await message.remove_reaction("2️⃣", self.client.user)
        await message.remove_reaction("3️⃣", self.client.user)
        await message.remove_reaction("4️⃣", self.client.user)
        await message.remove_reaction("5️⃣", self.client.user)

        application_collection = self.client.get_database_collection("applications")
        applications_query = [{}, {"status": "PENDING"}, {"status": "ACCEPTED"}, {"status": "REJECTED"}, {"status": "CANCELLED"}][["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"].index(applications_filter_reply)]
        applications = application_collection.find(applications_query)
        application_count = application_collection.count_documents(applications_query)
        page_index = 0

        if application_count == 0:
            no_applications_embed = self.client.create_embed(
                "No Applications",
                "No applications were found matching your query.",
                config.embed_error_color
            )

            return await message.edit(embed=no_applications_embed)

        loading_data_embed = self.client.create_embed(
            "Loading Data",
            "Currently fetching data from our database...",
            config.embed_info_color
        )

        await message.edit(embed=loading_data_embed)

        while True:
            application = applications[page_index]
            applicant = await self.client.fetch_member(application["member"])

            application_embed = self.client.create_embed(
                f"Application #{application['_id']}",
                f"Staff application from {applicant.name} ({applicant.mention}).",
                config.embed_info_color
            )

            application_embed.add_field(
                name="Gamemodes Selected:",
                value="None" if len(application["gamemodes"]) == 0 else ", ".join(application["gamemodes"]),
                inline=False
            )

            for question_number, question_answer in enumerate(application["answers"], 1):
                application_embed.add_field(
                    name=f"{question_number}. {config.application_questions[question_number - 1].splitlines()[1]}",
                    value=question_answer,
                    inline=False
                )

            application_embed.set_footer(text=f"Page {page_index + 1}/{application_count}")

            await message.edit(embed=application_embed)

            await message.add_reaction("⏮")
            await message.add_reaction("⬅")
            await message.add_reaction("🛑")
            await message.add_reaction("➡")
            await message.add_reaction("⏭")

            application_reply = await self.client.message_reaction(message, ctx.author, 300)

            if application_reply is None:
                return

            async def invalid_response():
                invalid_response_embed = self.client.create_embed(
                    "Invalid Response",
                    "The response that you provided to the question was not acceptable.",
                    config.embed_error_color
                )

                await message.edit(embed=invalid_response_embed)

            if application_reply not in ["⏮", "⬅", "🛑", "➡", "⏭"]:
                return await invalid_response()

            await message.remove_reaction(application_reply, ctx.author)

            if application_reply == "⏮":
                page_index = 0
            elif application_reply == "⬅":
                page_index -= 1
            elif application_reply == "🛑":
                await message.remove_reaction("⏮", ctx.guild.me)
                await message.remove_reaction("⬅", ctx.guild.me)
                await message.remove_reaction("🛑", ctx.guild.me)
                await message.remove_reaction("➡", ctx.guild.me)
                await message.remove_reaction("⏭", ctx.guild.me)
                return
            elif application_reply == "➡":
                page_index += 1
            elif application_reply == "⏭":
                page_index = application_count - 1

            if page_index == -1:
                page_index = application_count - 1

            if page_index == application_count:
                page_index = 0

    accept_details = command_details["accept"]

    @commands.command(
        name="accept",
        aliases=accept_details["aliases"],
        usage=accept_details["usage"],
        description=accept_details["description"],
        signature=accept_details["signature"])
    @commands.has_any_role(*accept_details["required_roles"])
    @commands.cooldown(accept_details["cooldown_rate"], accept_details["cooldown_per"])
    async def accept(self, ctx, application_id):
        application_collection = self.client.get_database_collection("applications")

        if application_collection.count_documents({"_id": application_id, "status": "PENDING"}) == 0:
            error_embed = self.client.create_embed(
                "Application Not Found",
                "No application with that ID was found in my database.",
                config.embed_error_color
            )

            return await ctx.reply(embed=error_embed)

        user = await self.client.fetch_user(application_collection.find_one({"_id": application_id})["member"])

        application_add_note_embed = self.client.create_embed(
            "Add Note to Application",
            "Would you like to write a note to the applicant regarding their application?",
            config.embed_info_color
        )

        application_add_note_message = await ctx.reply(embed=application_add_note_embed)

        await application_add_note_message.add_reaction("❌")
        await application_add_note_message.add_reaction("✅")

        application_add_note_reply = await self.client.message_reaction(application_add_note_message, ctx.author, 25)

        if application_add_note_reply is None:
            return

        async def invalid_response(message):
            invalid_response_embed = self.client.create_embed(
                "Invalid Response",
                "The response that you provided to the question was not acceptable.",
                config.embed_error_color
            )

            await message.reply(embed=invalid_response_embed)

        if application_add_note_reply not in ["❌", "✅"]:
            return await invalid_response(application_add_note_message)

        async def accept_application(last_reply, note=None):
            application_collection.update_one({"_id": application_id}, {"$set": {"status": "ACCEPTED"}})
            application_accept_embed = self.client.create_embed(
                "Application Accepted",
                "Your application to the OUT Guild has been accepted, congratulations!",
                config.embed_success_color
            )

            if note is not None:
                application_accept_embed.add_field(name="Note", value=note, inline=True)

            applicant_channel = await user.create_dm()

            try:
                await applicant_channel.send(embed=application_accept_embed)
                notification_sent = True
            except Forbidden:  # The user has DMs disabled
                notification_sent = False

            log_embed = self.client.create_embed(
                "Application Accepted",
                "An application was accepted by a moderator.",
                config.embed_info_color
            )

            log_embed.add_field(name="Application ID", value=application_id, inline=True)
            log_embed.add_field(name="Moderator", value=f"{ctx.author.name} ({ctx.author.mention})", inline=False)
            
            if note is not None:
                log_embed.add_field(name="Application Note", value=note, inline=True)

            if not notification_sent:
                log_embed.set_footer(text="The user did not receive a notification because their DMs are disabled.")

            log_channel = self.client.get_channel(config.channel_ids["applications"])
            await log_channel.send(embed=log_embed)

            success_embed = self.client.create_embed(
                "Application Accepted",
                f"Your acceptance of application #{application_id} was successful.",
                config.embed_success_color
            )

            success_embed.add_field(name="Application ID", value=application_id, inline=True)
            success_embed.add_field(name="Applicant", value=f"{user.name} ({user.mention})", inline=False)

            if note is not None:
                success_embed.add_field(name="Application Note", value=note, inline=True)

            if not notification_sent:
                success_embed.set_footer(text="The member did not receive a notification because their DMs are disabled.")

            return await last_reply.reply(embed=success_embed)

        if application_add_note_reply == "❌":
            await accept_application(application_add_note_message)
        else:  # A note will be added
            note_embed = self.client.create_embed(
                "Application Note",
                f"What note would you like to add to the acceptance of application #{application_id}?",
                config.embed_info_color
            )

            note_message = await application_add_note_message.reply(embed=note_embed)
            note_reply = await self.client.message_response(note_message, ctx.author, 60)

            if note_reply is None:
                return

            await accept_application(note_reply, note_reply.content)

    reject_details = command_details["reject"]

    @commands.command(
        name="reject",
        aliases=reject_details["aliases"],
        usage=reject_details["usage"],
        description=reject_details["description"],
        signature=reject_details["signature"])
    @commands.has_any_role(*reject_details["required_roles"])
    @commands.cooldown(reject_details["cooldown_rate"], reject_details["cooldown_per"])
    async def reject(self, ctx, application_id):
        application_collection = self.client.get_database_collection("applications")

        if application_collection.count_documents({"_id": application_id, "status": "PENDING"}) == 0:
            error_embed = self.client.create_embed(
                "Application Not Found",
                "No application with that ID was found in my database.",
                config.embed_error_color
            )

            return await ctx.reply(embed=error_embed)

        user = await self.client.fetch_user(application_collection.find_one({"_id": application_id})["member"])

        application_add_note_embed = self.client.create_embed(
            "Add Note to Application",
            "Would you like to write a note to the applicant regarding their application?",
            config.embed_info_color
        )

        application_add_note_message = await ctx.reply(embed=application_add_note_embed)

        await application_add_note_message.add_reaction("❌")
        await application_add_note_message.add_reaction("✅")

        application_add_note_reply = await self.client.message_reaction(application_add_note_message, ctx.author, 25)

        if application_add_note_reply is None:
            return

        async def invalid_response(message):
            invalid_response_embed = self.client.create_embed(
                "Invalid Response",
                "The response that you provided to the question was not acceptable.",
                config.embed_error_color
            )

            await message.reply(embed=invalid_response_embed)

        if application_add_note_reply not in ["❌", "✅"]:
            return await invalid_response(application_add_note_message)

        async def reject_application(last_reply, note=None):
            application_collection.update_one({"_id": application_id}, {"$set": {"status": "REJECTED"}})
            application_accept_embed = self.client.create_embed(
                "Application Rejection",
                "Your application to the OUT Guild has been rejected, you have the right to re-appy in 7 days time.",
                config.embed_error_color
            )

            if note is not None:
                application_accept_embed.add_field(name="Note", value=note, inline=True)

            applicant_channel = await user.create_dm()

            try:
                await applicant_channel.send(embed=application_accept_embed)
                notification_sent = True
            except Forbidden:  # The user has DMs disabled
                notification_sent = False

            log_embed = self.client.create_embed(
                "Application Rejected",
                "An application was rejected by a moderator.",
                config.embed_info_color
            )

            log_embed.add_field(name="Application ID", value=application_id, inline=True)
            log_embed.add_field(name="Moderator", value=f"{ctx.author.name} ({ctx.author.mention})", inline=False)

            if note is not None:
                log_embed.add_field(name="Application Note", value=note, inline=True)

            if not notification_sent:
                log_embed.set_footer(text="The user did not receive a notification because their DMs are disabled.")

            log_channel = self.client.get_channel(config.channel_ids["application-logs"])
            await log_channel.send(embed=log_embed)

            success_embed = self.client.create_embed(
                "Application Rejected",
                f"Your rejection of application #{application_id} was successful.",
                config.embed_success_color
            )

            success_embed.add_field(name="Application ID", value=application_id, inline=True)
            success_embed.add_field(name="Applicant", value=f"{user.name} ({user.mention})", inline=False)

            if note is not None:
                success_embed.add_field(name="Application Note", value=note, inline=True)

            if not notification_sent:
                success_embed.set_footer(text="The member did not receive a notification because their DMs are disabled.")

            return await last_reply.reply(embed=success_embed)

        if application_add_note_reply == "❌":
            await reject_application(application_add_note_message)
        else:  # A note will be added
            note_embed = self.client.create_embed(
                "Application Note",
                f"What note would you like to add to the acceptance of application #{application_id}?",
                config.embed_info_color
            )

            note_message = await application_add_note_message.reply(embed=note_embed)
            note_reply = await self.client.message_response(note_message, ctx.author, 60)

            if note_reply is None:
                return

            await reject_application(note_reply, note_reply.content)

    cancel_details = command_details["cancel"]

    @commands.command(
        name="cancel",
        aliases=cancel_details["aliases"],
        usage=cancel_details["usage"],
        description=cancel_details["description"],
        signature=cancel_details["signature"])
    @commands.has_any_role(*cancel_details["required_roles"])
    @commands.cooldown(cancel_details["cooldown_rate"], cancel_details["cooldown_per"])
    async def cancel(self, ctx, application_id):
        application_collection = self.client.get_database_collection("applications")

        if application_collection.count_documents({"_id": application_id, "status": "PENDING"}) == 0:
            error_embed = self.client.create_embed(
                "Application Not Found",
                "No application with that ID was found in my database.",
                config.embed_error_color
            )

            return await ctx.reply(embed=error_embed)

        user = await self.client.fetch_user(application_collection.find_one({"_id": application_id})["member"])

        async def cancel_application(last_reply):
            application_collection.update_one({"_id": application_id}, {"$set": {"status": "CANCELLED"}})
            log_embed = self.client.create_embed(
                "Application Rejected",
                "An application was rejected by a moderator.",
                config.embed_info_color
            )

            log_embed.add_field(name="Application ID", value=application_id, inline=True)
            log_embed.add_field(name="Moderator", value=f"{ctx.author.name} ({ctx.author.mention})", inline=False)

            log_channel = self.client.get_channel(config.channel_ids["applications"])
            await log_channel.send(embed=log_embed)

            success_embed = self.client.create_embed(
                "Application Rejected",
                f"Your rejection of application #{application_id} was successful.",
                config.embed_success_color
            )

            success_embed.add_field(name="Application ID", value=application_id, inline=True)
            success_embed.add_field(name="Applicant", value=f"{user.name} ({user.mention})", inline=False)

            return await last_reply.reply(embed=success_embed)

        await cancel_application(ctx.message)

async def setup(client):
    await client.add_cog(Applications(client), guilds=[discord.Object(id=503560012581568514)])
