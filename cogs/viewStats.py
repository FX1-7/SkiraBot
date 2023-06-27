import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands, pages
import datetime
from config import MAIN
import time
import aiosqlite
from utils.utils import utc_now
from config import GUILD_ID, TRACK_CHANNEL


class ViewStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(guild_ids=[GUILD_ID])
    async def alltimestats(self, ctx: discord.ApplicationContext, member: discord.Member):
        UserID = member.id
        async with aiosqlite.connect("data.db") as db:
            async with db.execute("SELECT * FROM AllTimeStats WHERE UserID = ?", (UserID,)) as UserStats:
                entry = await UserStats.fetchall()
                em = discord.Embed(title=f"🔊 {member.display_name}'s All Time Voice Stats 🔊", colour=MAIN,
                                   timestamp=discord.utils.utcnow())
                for detail in entry:
                    minutes, seconds = divmod(detail[2], 60)
                    hours, minutes = divmod(minutes, 60)
                    days, hours = divmod(hours, 24)
                    if days >= 1:
                        em.add_field(name="Channel:", value=f" <#{detail[1]}> Time: {int(days)} days, {int(hours)} hours,"
                                                            f" {int(minutes)} minutes, {round(seconds, 2)} seconds", inline=False)
                    else:
                        if hours >= 1:
                            em.add_field(name="Channel:", value=f" <#{detail[1]}> Time: {int(hours)} hours,"
                                                                f" {int(minutes)} minutes, {round(seconds, 2)} seconds", inline=False)
                        else:
                            if minutes >= 1:
                                em.add_field(name="Channel:", value=f" <#{detail[1]}> Time: {int(minutes)} minutes,"
                                                                    f" {round(seconds, 2)} seconds",
                                             inline=False)
                            else:
                                em.add_field(name="Channel:", value=f" <#{detail[1]}> Time: {round(seconds, 2)} seconds",
                                             inline=False)
                em.set_footer(text="These stats are updated on the first day of every month!")
            await ctx.respond(embed=em)

    @discord.slash_command(guild_ids=[GUILD_ID])
    async def weeklystats(self, ctx: discord.ApplicationContext, member: discord.Member):
        UserID = member.id
        async with aiosqlite.connect("data.db") as db:
            async with db.execute("SELECT * FROM WeeklyStats WHERE UserID = ?", (UserID,)) as UserStats:
                entry = await UserStats.fetchall()
                em = discord.Embed(title=f"🔊 {member.display_name}'s Weekly Voice Stats 🔊", colour=MAIN,
                                   timestamp=discord.utils.utcnow())
                for detail in entry:
                    minutes, seconds = divmod(detail[2], 60)
                    hours, minutes = divmod(minutes, 60)
                    days, hours = divmod(hours, 24)
                    if days >= 1:
                        em.add_field(name="Channel:",
                                     value=f" <#{detail[1]}> Time: {int(days)} days, {int(hours)} hours,"
                                           f" {int(minutes)} minutes, {round(seconds, 2)} seconds", inline=False)
                    else:
                        if hours >= 1:
                            em.add_field(name="Channel:", value=f" <#{detail[1]}> Time: {int(hours)} hours,"
                                                                f" {int(minutes)} minutes, {round(seconds, 2)} seconds",
                                         inline=False)
                        else:
                            if minutes >= 1:
                                em.add_field(name="Channel:", value=f" <#{detail[1]}> Time: {int(minutes)} minutes,"
                                                                    f" {round(seconds, 2)} seconds",
                                             inline=False)
                            else:
                                em.add_field(name="Channel:",
                                             value=f" <#{detail[1]}> Time: {round(seconds, 2)} seconds",
                                             inline=False)
            await ctx.respond(embed=em)

    @discord.slash_command(guild_ids=[GUILD_ID])
    async def monthlystats(self, ctx: discord.ApplicationContext, member: discord.Member):
        UserID = member.id
        async with aiosqlite.connect("data.db") as db:
            current_month = datetime.datetime.utcnow().month
            target_months = [(current_month - i) % 12 for i in range(3)]

            em = discord.Embed(title=f"🔊 {member.display_name}'s Monthly Voice Stats 🔊", colour=MAIN,
                               timestamp=discord.utils.utcnow())

            for target_month in target_months:
                async with db.execute("SELECT * FROM MonthlyStats WHERE UserID = ? AND Month = ?",
                                      (UserID, target_month)) as UserStats:
                    entry = await UserStats.fetchall()
                    month_name = datetime.date(1900, target_month, 1).strftime("%B")
                    month_stats = ""

                    for detail in entry:
                        minutes, seconds = divmod(detail[2], 60)
                        hours, minutes = divmod(minutes, 60)
                        days, hours = divmod(hours, 24)

                        if days >= 1:
                            month_stats += f"Channel: <#{detail[1]}> Time: {int(days)} days, {int(hours)} hours," \
                                           f" {int(minutes)} minutes, {round(seconds, 2)} seconds\n"
                        elif hours >= 1:
                            month_stats += f"Channel: <#{detail[1]}> Time: {int(hours)} hours, {int(minutes)} minutes," \
                                           f" {round(seconds, 2)} seconds\n"
                        elif minutes >= 1:
                            month_stats += f"Channel: <#{detail[1]}> Time: {int(minutes)} minutes," \
                                           f" {round(seconds, 2)} seconds\n"
                        else:
                            month_stats += f"Channel: <#{detail[1]}> Time: {round(seconds, 2)} seconds\n"

                    if month_stats:
                        em.add_field(name=f"{month_name}", value=month_stats, inline=False)
                    else:
                        em.add_field(name=f"{month_name}", value="No data available", inline=False)

        await ctx.respond(embed=em)

    @discord.slash_command(guild_ids=[GUILD_ID])
    async def tracking(self, ctx: discord.ApplicationContext):
        em = discord.Embed(title=f"Current Tracking",
                           colour=MAIN, timestamp=discord.utils.utcnow())
        em.add_field(name="Channels:", value="", inline=False)
        for x in TRACK_CHANNEL:
            channel_id = ctx.guild.get_channel(x).id
            em.add_field(name="", value=f"\n<#{channel_id}> ", inline=False)

        await ctx.respond(embed=em)

def setup(bot):
    bot.add_cog(ViewStats(bot))
