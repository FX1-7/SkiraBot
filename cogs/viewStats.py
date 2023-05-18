import discord
from discord.ext import commands
import datetime as dt
from config import MAIN
import time
import aiosqlite
from utils.utils import utc_now
from config import GUILD_ID


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
            async with db.execute("SELECT * FROM MonthlyStats WHERE UserID = ?", (UserID,)) as UserStats:
                entry = await UserStats.fetchall()
                em = discord.Embed(title=f"🔊 {member.display_name}'s Monthly Voice Stats 🔊", colour=MAIN,
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


def setup(bot):
    bot.add_cog(ViewStats(bot))
