import datetime
import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands, pages
from config import MAIN
import aiosqlite


class CompanyStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.alltime_pages = []
        self.weekly_pages = []
        self.monthly_pages = []

    async def allstats(self, role_id, guild_id):
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

                    guild = self.bot.get_guild(guild_id)
                    member = guild.get_member(user_id)
                    if member is None:
                        continue

                    if discord.utils.get(member.roles, id=role_id) is None:
                        continue

                    if user_id not in user_stats:
                        user_stats[user_id] = {}

                    if channel_id in user_stats[user_id]:
                        user_stats[user_id][channel_id] += time_spent
                    else:
                        user_stats[user_id][channel_id] = time_spent

                em = discord.Embed(title="🔊 All Time Voice Stats 🔊", colour=MAIN, timestamp=discord.utils.utcnow())

                for user_id, stats in user_stats.items():
                    total_time_spent = sum(stats.values())
                    hours = round(total_time_spent / 3600, 2)
                    days = round(hours / 24, 2)

                    user_name = self.bot.get_user(user_id)
                    time_string = ""
                    if days > 0:
                        time_string += f"{int(days)} days, "
                    if hours > 0:
                        time_string += f"{int(hours)} hours."
                    em.add_field(name=f"User ID: {user_name.display_name}", value=f"**Total Play Time:** {time_string}",
                                 inline=False)

            self.alltime_pages.append(em)

    async def weeklystats(self, role_id, guild_id):
        async with aiosqlite.connect("data.db") as db:
            query = """
                SELECT UserID, SUM(TimeSpent) AS TotalTimeSpent
                FROM WeeklyStats
                GROUP BY UserID
            """
            async with db.execute(query) as UserStats:
                entry = await UserStats.fetchall()
                user_stats = {}

                for detail in entry:
                    user_id = detail[0]
                    time_spent = detail[1]

                    guild = self.bot.get_guild(guild_id)
                    member = guild.get_member(user_id)
                    if member is None:
                        continue

                    if discord.utils.get(member.roles, id=role_id) is None:
                        continue

                    user_stats[user_id] = time_spent

                em = discord.Embed(title="🔊 Weekly Voice Stats 🔊", colour=MAIN, timestamp=discord.utils.utcnow())

                for user_id, time_spent in user_stats.items():
                    hours = round(time_spent / 3600, 2)
                    days = round(hours / 24, 2)

                    user_name = self.bot.get_user(user_id)
                    time_string = ""
                    if days > 0:
                        time_string += f"{int(days)} days, "
                    if hours > 0:
                        time_string += f"{int(hours)} hours"

                    em.add_field(name=f"User ID: {user_name.display_name}", value=f"Total Time Spent: {time_string}",
                                 inline=False)

                self.weekly_pages.append(em)

    async def monthlystats(self, role_id, guild_id):
        async with aiosqlite.connect("data.db") as db:
            current_month = datetime.datetime.utcnow().month
            target_months = [(current_month - i) % 12 for i in range(3)]

            em = discord.Embed(title="🔊 Monthly Voice Stats 🔊", colour=MAIN, timestamp=discord.utils.utcnow())

            for target_month in target_months:
                async with db.execute(
                        "SELECT UserID, SUM(TimeSpent) AS TotalTimeSpent FROM MonthlyStats WHERE Month = ? GROUP BY UserID",
                        (target_month,)) as MonthlyStats:
                    monthly_entry = await MonthlyStats.fetchall()
                    monthly_stats = {}

                    for detail in monthly_entry:
                        user_id = detail[0]
                        time_spent = detail[1]
                        monthly_stats[user_id] = time_spent

                    if target_month == current_month:
                        async with db.execute("SELECT UserID, TimeSpent FROM WeeklyStats") as WeeklyStats:
                            weekly_entry = await WeeklyStats.fetchall()

                            for detail in weekly_entry:
                                user_id = detail[0]
                                time_spent = detail[1]

                                if user_id in monthly_stats:
                                    monthly_stats[user_id] += time_spent
                                else:
                                    monthly_stats[user_id] = time_spent

                    month_name = datetime.date(1900, target_month, 1).strftime("%B")
                    month_stats = []

                    for user_id, time_spent in monthly_stats.items():
                        guild = self.bot.get_guild(guild_id)
                        member = guild.get_member(user_id)
                        if member is None:
                            continue

                        if discord.utils.get(member.roles, id=role_id) is None:
                            continue

                        hours = round(time_spent / 3600, 2)
                        days = round(hours / 24, 2)

                        if days >= 1:
                            month_stats.append(
                                f"**User: {member.display_name}**, Time: {int(days)} days, {int(hours)} hours.")
                        elif hours >= 1:
                            month_stats.append(f"**User: {member.display_name}**, Time: {int(hours)} hours.")

                    if month_stats:
                        month_stats_string = "\n".join(month_stats)
                        em.add_field(name=f"{month_name}", value=month_stats_string, inline=False)
                        em.set_footer(text=f"Month: {month_name}")
                    else:
                        em.add_field(name=f"{month_name}", value="No data available", inline=False)
                        em.set_footer(text=f"Month: {month_name}")

            self.monthly_pages.append(em)

    def get_alltime_pages(self):
        return self.alltime_pages

    def get_weekly_pages(self):
        return self.weekly_pages

    def get_monthly_pages(self):
        return self.monthly_pages

    def get_pages(self):
        return self.pages

    skirastats = SlashCommandGroup("companystats", "Shows all time stats for all users in x role with different commands"
                                                   "for different time scales.")

    @skirastats.command(name="alltime", description="Shows all time stats for all users in x role")
    async def alltime(self, ctx: discord.ApplicationContext, role: discord.Role):
        self.alltime_pages = []

        await self.allstats(role.id, ctx.guild_id)

        paginator = pages.Paginator(pages=self.get_alltime_pages())
        await paginator.respond(ctx.interaction)

    @skirastats.command(name="weekly", description="Shows Weekly time stats for all users in x role")
    async def weekly(self, ctx: discord.ApplicationContext, role: discord.Role):
        self.weekly_pages = []

        await self.weeklystats(role.id, ctx.guild_id)

        paginator = pages.Paginator(pages=self.get_weekly_pages())
        await paginator.respond(ctx.interaction)

    @skirastats.command(name="monthly", description="Shows Weekly time stats for all users in x role")
    async def monthly(self, ctx: discord.ApplicationContext, role: discord.Role):
        self.monthly_pages = []

        await self.monthlystats(role.id, ctx.guild_id)

        paginator = pages.Paginator(pages=self.get_monthly_pages())
        await paginator.respond(ctx.interaction)


def setup(bot):
    bot.add_cog(CompanyStats(bot))

