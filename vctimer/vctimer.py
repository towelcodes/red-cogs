# pyright: reportUnknownMemberType=false
# pyright: reportUnusedCallResult=false
# pyright: reportExplicitAny=false
# pyright: reportUnknownVariableType=false
import asyncio
from asyncio.tasks import Task
from typing import Any, Dict, Union
from typing_extensions import override
import discord
from discord.enums import ChannelType
from redbot.core import commands, Config
from discord import Embed

class VcTimer(commands.Cog):
    def __init__(self, bot: commands.Bot):  # pyright: ignore[reportMissingSuperCall]
        self.bot: commands.Bot = bot
        self.config: Config = Config.get_conf(self, identifier=90834609231)
        self.check_vc_task: Union[Task[None],  None] = None
        default_guild: Dict[str, Any] = {
            "monitor": [],
            "users": {},
        }
        self.config.register_guild(**default_guild)

    def _format_time(self, seconds: int) -> str:
        """Format seconds into a human-readable time string."""
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)

        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

    async def check_vc(self):
        while True:
            try:
                for guild in self.bot.guilds:
                    monitored_channels = await self.config.guild(guild).monitor()

                    if not monitored_channels:
                        continue
                    async with self.config.guild(guild).users() as users:
                        for channel_id in monitored_channels:
                            channel = guild.get_channel(channel_id)
                            if not channel or channel.type != ChannelType.voice:
                                continue

                            for member in channel.members:
                                print("channel member:", member)
                                if member.bot:
                                    continue

                                user_id = str(member.id)

                                if user_id not in users:
                                    users[user_id] = 10  # 10 seconds for first time
                                    print(users[user_id])
                                else:
                                    users[user_id] += 10  # Increment by 10 seconds
                                    print(users[user_id])
            except Exception as e:
                print(f"error in check_vc: {e}")
            await asyncio.sleep(10)

    @commands.guild_only()
    @commands.command()
    async def vc_longest_time(self, ctx: commands.Context):
        assert ctx.guild
        users = await self.config.guild(ctx.guild).users()

        if not users:
            await ctx.send("No voice channel data available yet.")
            return
        sorted_users = sorted(users.items(), key=lambda x: int(x[1]), reverse=True)
        embed = Embed(
            title="🎤 Voice Channel Leaderboard",
            description="Top users by total time in monitored voice channels",
            color=0x00ff00
        )
        for i, (user_id, total_time) in enumerate(sorted_users[:5]):
            try:
                user = ctx.guild.get_member(int(user_id))
                time_str = self._format_time(int(total_time))

                if user:
                    embed.add_field(
                        name=f"#{i+1} {user.display_name}",
                        value=f"⏱️ {time_str}",
                        inline=False
                    )
                else:
                    # user left the server, but we can still show their ID
                    embed.add_field(
                        name=f"#{i+1} User ID: {user_id}",
                        value=f"⏱️ {time_str} (User left server)",
                        inline=False
                    )
            except ValueError:
                continue

        if not embed.fields:
            embed.description = "No valid user data found."

        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.admin_or_can_manage_channel()
    @commands.command()
    async def vc_status(self, ctx: commands.Context):
        assert ctx.guild
        monitored_channels = await self.config.guild(ctx.guild).monitor()

        if not monitored_channels:
            await ctx.send("No voice channels are being monitored.")
            return

        embed = Embed(
            title="🔍 Voice Channel Status",
            description="Current monitoring status",
            color=0x0099ff
        )

        total_active_users = 0

        for channel_id in monitored_channels:
            channel = ctx.guild.get_channel(channel_id)

            if not channel or channel.type != ChannelType.voice:
                embed.add_field(
                    name=f"❌ Channel ID: {channel_id}",
                    value="Channel not found or not a voice channel",
                    inline=False
                )
                continue

            human_members = [m for m in channel.members if not m.bot]
            member_count = len(human_members)
            total_active_users += member_count

            if member_count > 0:
                member_list = ", ".join([m.display_name for m in human_members[:5]])
                if member_count > 5:
                    member_list += f" +{member_count - 5} more"

                embed.add_field(
                    name=f"🎤 {channel.name}",
                    value=f"**{member_count}** user{'s' if member_count != 1 else ''}: {member_list}",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"💤 {channel.name}",
                    value="No users currently",
                    inline=False
                )

        embed.set_footer(text=f"Total active users: {total_active_users}")
        await ctx.send(embed=embed)

    @override
    async def cog_load(self):
        print("adding task")
        self.check_vc_task = self.bot.loop.create_task(self.check_vc())
        print("created task")

    @override
    async def cog_unload(self):
        if self.check_vc_task != None:
            self.check_vc_task.cancel()
            print("cancelled task")

    @commands.guild_only()
    @commands.admin_or_can_manage_channel()
    @commands.command()
    async def add_monitor(self, ctx: commands.Context, channel: discord.VoiceChannel):
        assert ctx.guild
        channel_id = channel.id
        async with self.config.guild(ctx.guild).monitor() as monitors:
            if channel_id not in monitors:
                monitors.append(channel_id)
                await ctx.send(f"Voice channel {channel.name} has been added to the monitor list.")
            else:
                await ctx.send(f"Voice channel {channel.name} is already being monitored.")

    @commands.guild_only()
    @commands.admin_or_can_manage_channel()
    @commands.command()
    async def remove_monitor(self, ctx: commands.Context, channel: discord.VoiceChannel):
        assert ctx.guild
        channel_id = channel.id
        async with self.config.guild(ctx.guild).monitor() as monitors:
            if channel_id in monitors:
                monitors.remove(channel_id)
                await ctx.send(f"Voice channel {channel.name} has been removed from the monitor list.")
            else:
                await ctx.send(f"Voice channel {channel.name} is not being monitored.")
