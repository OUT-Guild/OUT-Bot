import discord_module as discord

import discord
from discord.ext import commands

import config

class Logs(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.invitesBefore = None
        self.lastAuditID = None

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="-Starbuck"))
        guild = self.client.get_guild(503560012581568514)
        self.invitesBefore = await guild.invites()
        self.invitesBefore.append(await guild.vanity_invite())

    @commands.Cog.listener()
    async def on_member_join(self, member):
        invitesAfter = await member.guild.invites()
        invitesAfter.append(await member.guild.vanity_invite())

        code = "Unable to Trace"
        inviter = "Unable to Trace"

        def traceInvite(inviteList, code):
            for invite in inviteList:
                if invite.code == code:
                    return invite

        for invite in self.invitesBefore:
            if invite.uses < traceInvite(invitesAfter, invite.code).uses:
                if invite.code == "out":
                    code = invite.code.upper()
                    inviter = self.client.user.mention
                else:
                    code = invite.code.upper()
                    inviter = invite.inviter.mention

                self.invitesBefore = await member.guild.invites()
                self.invitesBefore.append(await member.guild.vanity_invite())

        embed = discord.Embed(
            title="Member {} | {}".format(member.guild.member_count, member.name),
            color=discord.Color.green()
        )

        embed.add_field(name="Member", value=member.mention, inline=False)
        embed.add_field(name="Invite Code", value=code, inline=False)
        embed.add_field(name="Inviter", value=inviter, inline=False)
        embed.set_author(name=member.name, icon_url=member.avatar.url)

        channel = self.client.get_channel(config.channel_ids["join_leave_logs"])
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(
            title="Member Left",
            color=discord.Color.red()
        )

        embed.add_field(name="Member", value=member.mention, inline=False)
        embed.set_author(name=member.name, icon_url=member.avatar.url)

        channel = self.client.get_channel(config.channel_ids["join_leave_logs"])
        await channel.send(embed=embed)

        self.invitesBefore = await member.guild.invites()
        self.invitesBefore.append(await member.guild.vanity_invite())

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        try:
            guild = self.client.get_guild(payload.guild_id)
            message = payload.cached_message

            embed = discord.Embed(
                title="Message Deleted",
                color=discord.Color.red()
            )

<<<<<<< Updated upstream
            embed.add_field(name="Member", value=message.author.mention, inline=False)
            embed.add_field(name="Channel", value=message.channel.mention, inline=False)
            embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
=======
        embed.add_field(name="Member", value=message.author.mention, inline=False)
        embed.add_field(name="Channel", value=message.channel.mention, inline=False)
        embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
>>>>>>> Stashed changes

            if len(message.content) > 0:
                embed.add_field(name="Message", value=message.content, inline=False)

            async for entry in guild.audit_logs(limit=1):
                if entry.action == discord.AuditLogAction.message_delete and self.lastAuditID != entry.id:
                    self.lastAuditID = entry.id
                    embed.add_field(name="Deleter", value=entry.user.mention, inline=False)
                else:
                    embed.add_field(name="Deleter",
                                    value=f"Either {message.author.mention} or {self.client.user.mention}",
                                    inline=False)

            for attachment in message.attachments:
                embed.set_image(url=attachment.proxy_url)
        except:
            channel = self.client.get_channel(payload.channel_id)

            embed = discord.Embed(
                title="Message Deleted",
                color=discord.Color.red()
            )

            embed.add_field(name="Member", value="Unable to Trace", inline=False)
            embed.add_field(name="Channel", value=channel.mention, inline=False)
            embed.add_field(name="Message", value="Unable to Trace", inline=False)

            async for entry in guild.audit_logs(limit=1):
                if entry.action == discord.AuditLogAction.message_delete and self.lastAuditID != entry.id:
                    self.lastAuditID = entry.id
                    embed.add_field(name="Deleter", value=entry.user.mention, inline=False)
                else:
                    embed.add_field(name="Deleter", value="Unable to Trace", inline=False)

        channel = self.client.get_channel(config.channel_ids["message_logs"])
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload):
        guild = self.client.get_guild(payload.guild_id)
        channel = self.client.get_channel(payload.channel_id)

        embed = discord.Embed(
            title="Bulk Messages Deleted",
            color=discord.Color.red()
        )

        embed.add_field(name="Amount", value=len(payload.message_ids), inline=False)
        embed.add_field(name="Channel", value=channel.mention, inline=False)

        async for entry in guild.audit_logs(limit=1):
            if entry.action == discord.AuditLogAction.message_bulk_delete and self.lastAuditID != entry.id:
                self.lastAuditID = entry.id
                embed.add_field(name="Deleter", value=entry.user.mention, inline=False)
            else:
                embed.add_field(name="Deleter", value="Unable to Trace", inline=False)

        channel = self.client.get_channel(config.channel_ids["message_logs"])
        await channel.send(embed=embed)
        runLoops = 0

        try:
            for cached_message in payload.cached_messages:
                message = cached_message

<<<<<<< Updated upstream
                embed = discord.Embed(
                    title="Message Deleted | {} of {}".format(payload.cached_messages.index(cached_message) + 1,
                                                              len(payload.cached_messages)),
                    color=discord.Color.red()
                )
=======
            embed.add_field(name="Member", value=message.author.mention, inline=False)
            embed.add_field(name="Message", value=message.content, inline=False)
            embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
>>>>>>> Stashed changes

                embed.add_field(name="Member", value=message.author.mention, inline=False)
                embed.add_field(name="Message", value=message.content, inline=False)
                embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)

                for attachment in message.attachments:
                    embed.add_field(name="Attachment #{}".format(message.attachments.index(attachment) + 1),
                                    value=attachment.url, inline=False)

                channel = self.client.get_channel(config.channel_ids["message_logs"])
                await channel.send(embed=embed)

                runLoops += 1
        except:
            for message in range(len(payload.message_ids)):
                embed = discord.Embed(
                    title="Message Deleted | {} of {}".format(message + runLoops + 1, len(payload.message_ids)),
                    color=discord.Color.red()
                )

                embed.add_field(name="Member", value="Unable to Trace", inline=False)
                embed.add_field(name="Message", value="Unable to Trace", inline=False)

                channel = self.client.get_channel(config.channel_ids["message_logs"])
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        try:
            message = payload.cached_message
            channel = self.client.get_channel(payload.channel_id)

            if message.author.bot:
                return

            embed = discord.Embed(
                title="Message Edited",
                color=discord.Color.orange()
            )

<<<<<<< Updated upstream
            embed.add_field(name="Member", value=message.author.mention, inline=False)
            embed.add_field(name="Channel", value=channel.mention, inline=False)
            embed.add_field(name="Before", value=message.content, inline=False)
            embed.add_field(name="After", value=payload.data["content"], inline=False)
            embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
        except:
            channel = self.client.get_channel(payload.channel_id)

            embed = discord.Embed(
                title="Message Edited",
                color=discord.Color.orange()
            )

            embed.add_field(name="Member", value="Unable to Trace", inline=False)
            embed.add_field(name="Channel", value=channel.mention, inline=False)
            embed.add_field(name="Before", value="Unable to Trace", inline=False)
            embed.add_field(name="After", value="Unable to Trace", inline=False)
=======
        embed.add_field(name="Member", value=before.author.mention, inline=False)
        embed.add_field(name="Channel", value=channel.mention, inline=False)
        embed.add_field(name="Before", value=before.content, inline=False)
        embed.add_field(name="After", value=after.content, inline=False)
        embed.set_author(name=before.author.name, icon_url=before.author.avatar.url)
>>>>>>> Stashed changes

        channel = self.client.get_channel(config.channel_ids["message_logs"])
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not before.afk and after.afk:
            embed = discord.Embed(
                title="Member Went AFK",
                color=discord.Color.blue()
            )

            embed.add_field(name="Member", value=member.mention, inline=False)
            embed.add_field(name="Channel", value=after.channel.mention, inline=False)
        elif before.afk and not after.afk:
            embed = discord.Embed(
                title="Member Returned From AFK",
                color=discord.Color.blue()
            )

            embed.add_field(name="Member", value=member.mention, inline=False)
            embed.add_field(name="Channel", value=after.channel.mention, inline=False)
        elif before.channel is None:
            embed = discord.Embed(
                title="Member Joined Channel",
                color=discord.Color.green()
            )

            embed.add_field(name="Member", value=member.mention, inline=False)
            embed.add_field(name="Channel", value=after.channel.mention, inline=False)
        elif after.channel is None:
            embed = discord.Embed(
                title="Member Left Channel",
                color=discord.Color.red()
            )

            embed.add_field(name="Member", value=member.mention, inline=False)
            embed.add_field(name="Channel", value=before.channel.mention, inline=False)
        elif not before.deaf and after.deaf:
            embed = discord.Embed(
                title="Member Deafened",
                color=discord.Color.red()
            )

            embed.add_field(name="Member", value=member.mention, inline=False)
            embed.add_field(name="Channel", value=after.channel.mention, inline=False)

            async for entry in member.guild.audit_logs(limit=1):
                if entry.action == discord.AuditLogAction.member_update and self.lastAuditID != entry.id:
                    self.lastAuditID = entry.id
                    embed.add_field(name="Deafened By", value=entry.user.mention, inline=False)
                else:
                    embed.add_field(name="Deafened By", value="Unable to Trace", inline=False)
        elif before.deaf and not after.deaf:
            embed = discord.Embed(
                title="Member Undeafened",
                color=discord.Color.green()
            )

            embed.add_field(name="Member", value=member.mention, inline=False)
            embed.add_field(name="Channel", value=after.channel.mention, inline=False)

            async for entry in member.guild.audit_logs(limit=1):
                if entry.action == discord.AuditLogAction.member_update and self.lastAuditID != entry.id:
                    self.lastAuditID = entry.id
                    embed.add_field(name="Undeafened By", value=entry.user.mention, inline=False)
                else:
                    embed.add_field(name="Undeafened By", value="Unable to Trace", inline=False)
        elif not before.mute and after.mute:
            embed = discord.Embed(
                title="Member Muted",
                color=discord.Color.red()
            )

            embed.add_field(name="Member", value=member.mention, inline=False)
            embed.add_field(name="Channel", value=after.channel.mention, inline=False)

            async for entry in member.guild.audit_logs(limit=1):
                if entry.action == discord.AuditLogAction.member_update and self.lastAuditID != entry.id:
                    self.lastAuditID = entry.id
                    embed.add_field(name="Muted By", value=entry.user.mention, inline=False)
                else:
                    embed.add_field(name="Muted By", value="Unable to Trace", inline=False)
        elif before.mute and not after.mute:
            embed = discord.Embed(
                title="Member Unmuted",
                color=discord.Color.green()
            )

            embed.add_field(name="Member", value=member.mention, inline=False)
            embed.add_field(name="Channel", value=after.channel.mention, inline=False)

            async for entry in member.guild.audit_logs(limit=1):
                if entry.action == discord.AuditLogAction.member_update and self.lastAuditID != entry.id:
                    self.lastAuditID = entry.id
                    embed.add_field(name="Unmuted By", value=entry.user.mention, inline=False)
                else:
                    embed.add_field(name="Unmuted By", value="Unable to Trace", inline=False)
        elif not before.self_deaf and after.self_deaf:
            embed = discord.Embed(
                title="Member Deafened",
                color=discord.Color.red()
            )

            embed.add_field(name="Member", value=member.mention, inline=False)
            embed.add_field(name="Channel", value=after.channel.mention, inline=False)
            embed.add_field(name="Deafened By", value=member.mention, inline=False)
        elif before.self_deaf and not after.self_deaf:
            embed = discord.Embed(
                title="Member Undeafened",
                color=discord.Color.green()
            )

            embed.add_field(name="Member", value=member.mention, inline=False)
            embed.add_field(name="Channel", value=after.channel.mention, inline=False)
            embed.add_field(name="Undeafened By", value=member.mention, inline=False)
        elif not before.self_mute and after.self_mute:
            embed = discord.Embed(
                title="Member Muted",
                color=discord.Color.red()
            )

            embed.add_field(name="Member", value=member.mention, inline=False)
            embed.add_field(name="Channel", value=after.channel.mention, inline=False)
            embed.add_field(name="Muted By", value=member.mention, inline=False)
        elif before.self_mute and not after.self_mute:
            embed = discord.Embed(
                title="Member Unmuted",
                color=discord.Color.green()
            )

            embed.add_field(name="Member", value=member.mention, inline=False)
            embed.add_field(name="Channel", value=after.channel.mention, inline=False)
            embed.add_field(name="Unmuted By", value=member.mention, inline=False)
        elif not before.self_stream and after.self_stream:
            embed = discord.Embed(
                title="Member Started Streaming",
                color=discord.Color.green()
            )

            embed.add_field(name="Member", value=member.mention, inline=False)
            embed.add_field(name="Channel", value=after.channel.mention, inline=False)
        elif before.self_stream and not after.self_stream:
            embed = discord.Embed(
                title="Member Stopped Streaming",
                color=discord.Color.red()
            )

            embed.add_field(name="Member", value=member.mention, inline=False)
            embed.add_field(name="Channel", value=after.channel.mention, inline=False)
        elif not before.self_video and after.self_video:
            embed = discord.Embed(
                title="Member Started Their Camera",
                color=discord.Color.green()
            )

            embed.add_field(name="Member", value=member.mention, inline=False)
            embed.add_field(name="Channel", value=after.channel.mention, inline=False)
        elif before.self_video and not after.self_video:
            embed = discord.Embed(
                title="Member Stopped Their Camera",
                color=discord.Color.red()
            )

            embed.add_field(name="Member", value=member.mention, inline=False)
            embed.add_field(name="Channel", value=after.channel.mention, inline=False)

        embed.set_author(name=member.name, icon_url=member.avatar.url)

        channel = self.client.get_channel(config.channel_ids["voice_logs"])
        await channel.send(embed=embed)

async def setup(client):
    await client.add_cog(Logs(client), guilds=[discord.Object(id=503560012581568514)])
