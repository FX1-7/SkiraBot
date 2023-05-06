import discord
from discord.ext import commands
import datetime as dt
from config import MAIN
import time
import aiosqlite
from utils.utils import utc_now


class ViewStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def AllTimeStats(self, ctx: discord.ApplicationContext, member: discord.Member):
        UserID = member.id
        async with aiosqlite.connect("data.db") as db:
                async with db.execute("SELECT * FROM AllTimeStats WHERE UserID = ?", (UserID,)) as UserStats:
                    entry = await UserStats.fetchall()
                    for detail in entry:
                        em = discord.Embed(title=f"{member.display_name}'s All Time Voice Stats", colour=MAIN,
                                           timestamp=discord.utils.utcnow(),
                                           description=f"Channel: <#{detail[1]}>, Time: {detail[2]}")
                    await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(ViewStats(bot))
