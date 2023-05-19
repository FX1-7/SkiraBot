import datetime
import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands, pages
from config import MAIN
import aiosqlite


class CompanyStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pages = []

    async def fetchstats(self, role_id):
        async with aiosqlite.connect("data.db") as db:
            query = """
                        SELECT UserID, ChannelID, SUM(TimeSpent) AS TotalTimeSpent
                        FROM (
                            SELECT UserID, ChannelID, TimeSpent FROM AllTimeStats
                            UNION ALL
                            SELECT UserID, ChannelID, TimeSpent FROM WeeklyStats
                            UNION ALL
                            SELECT UserID, ChannelID, TimeSpent FROM MonthlyStats
                        ) AS CombinedStats
                        GROUP BY UserID, ChannelID
                    """
            async with db.execute(query) as UserStats:
                entry = await UserStats.fetchall()
                user_stats = {}

                for detail in entry:
                    user_id = detail[0]
                    channel_id = detail[1]
                    time_spent = detail[2]
                    print(user_stats)
                    print(user_id)

                    member = discord.utils.get(self.bot.get_all_members(), id=user_id)
                    if member is None:
                        continue

                    if discord.utils.get(member.roles, id=role_id) is None:
                        continue

                    if user_id not in user_stats:
                        print("Testing")
                        user_stats[user_id] = {}
                        print(user_stats[user_id])

                    if channel_id in user_stats[user_id]:
                        user_stats[user_id][channel_id] += time_spent
                    else:
                        user_stats[user_id][channel_id] = time_spent


                em = discord.Embed(title="🔊 Skira Company All Time Stats Voice Stats 🔊", colour=discord.Colour.blue(),
                                   timestamp=discord.utils.utcnow())
                em.set_footer(text="These stats are updated on the first day of every month!")

                for user_id, stats in user_stats.items():
                    user_channels = []

                    for channel_id, time_spent in stats.items():
                        minutes, seconds = divmod(time_spent, 60)
                        hours, minutes = divmod(minutes, 60)
                        days, hours = divmod(hours, 24)

                        print(channel_id)

                        user_channels.append(
                            f"**Channel:** <#{channel_id}>, Time Spent: {int(days)} days, {int(hours)} hours,"
                            f" {int(minutes)} minutes, {int(seconds)} seconds")
                    user_name = self.bot.get_user(user_id)
                    em.add_field(
                        name=f"User ID: {user_name.display_name}", value="\n".join(user_channels), inline=False)

                self.pages.append(em)

    def get_pages(self):
        return self.pages

    skirastats = SlashCommandGroup("companystats", "Shows all time stats for all users in skira company")

    @skirastats.command(name="alltime", description="Shows all time stats for all users in skira company")
    async def alltime(self, ctx: discord.ApplicationContext, role: discord.Role):
        self.pages = []

        await self.fetchstats(role.id)

        for page in self.pages:
            await ctx.respond(embed=page)


def setup(bot):
    bot.add_cog(CompanyStats(bot))

