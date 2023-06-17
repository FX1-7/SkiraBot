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
        guild = self.bot.get_guild(guild_id)
        role = guild.get_role(role_id)
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
                em = discord.Embed(title=f"🔊 All Time Voice Stats - {role} 🔊", colour=MAIN,
                                  timestamp=discord.utils.utcnow())
                em_list = []

                for user_id, stats in user_stats.items():
                    member = guild.get_member(user_id)
                    total_time_spent = sum(stats.values())
                    minutes, seconds = divmod(total_time_spent, 60)
                    hours, minutes = divmod(minutes, 60)

                    if hours >= 1:
                        time_string = f"{int(hours)} hours."
                        em.add_field(name=f"User ID: {member.display_name}",
                                     value=f"**Total Play Time:** {time_string}", inline=False)
                        if len(em.fields) >= 25:
                            em_list.append(em)
                            em = discord.Embed(title=f"🔊 All Time Voice Stats - {role} 🔊", colour=MAIN,
                                               timestamp=discord.utils.utcnow())

                if len(em.fields) > 0:
                    em_list.append(em)

                for em in em_list:
                    page = pages.Page(content="", embeds=[em])
                    self.alltime_pages.append(page)

    async def weeklystats(self, role_id, guild_id):
        guild = self.bot.get_guild(guild_id)
        role = guild.get_role(role_id)
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

                    member = guild.get_member(user_id)
                    if member is None:
                        continue

                    if discord.utils.get(member.roles, id=role_id) is None:
                        continue

                    user_stats[user_id] = time_spent

                em = discord.Embed(title=f"🔊 Weekly Voice Stats - {role} 🔊", colour=MAIN,
                                   timestamp=discord.utils.utcnow())

                for user_id, time_spent in user_stats.items():
                    minutes, seconds = divmod(time_spent, 60)
                    hours, minutes = divmod(minutes, 60)
                    days, hours = divmod(hours, 24)
                    days = round(days, 2)
                    hours = round(hours, 2)

                    user_name = guild.get_member(user_id)
                    time_string = ""
                    if hours >= 1:
                        time_string += f"{int(hours)} hours."

                    if hours or days >= 1:
                        em.add_field(
                            name=f"User ID: {user_name.display_name}",
                            value=f"Total Time Spent: {time_string}",
                            inline=False
                        )

                self.weekly_pages.append(em)

    async def monthlystats(self, role_id, guild_id):
        guild = self.bot.get_guild(guild_id)
        role = guild.get_role(role_id)
        async with aiosqlite.connect("data.db") as db:
            current_month = datetime.datetime.utcnow().month
            target_months = [(current_month - i) % 12 for i in range(3)]

            em = discord.Embed(title=f"🔊 Monthly Voice Stats - {role} 🔊", colour=MAIN, timestamp=discord.utils.utcnow())

            monthly_stats = {}

            for target_month in target_months:
                async with db.execute(
                        "SELECT UserID, SUM(TimeSpent) AS TotalTimeSpent FROM MonthlyStats WHERE Month = ? GROUP BY UserID",
                        (target_month,)) as MonthlyStats:
                    monthly_entry = await MonthlyStats.fetchall()

                    month_stats = {}

                    for detail in monthly_entry:
                        user_id = detail[0]
                        time_spent = detail[1]
                        month_stats[user_id] = time_spent

                    if target_month == current_month:
                        async with db.execute("SELECT UserID, TimeSpent FROM WeeklyStats") as WeeklyStats:
                            weekly_entry = await WeeklyStats.fetchall()

                            for detail in weekly_entry:
                                user_id = detail[0]
                                time_spent = detail[1]

                                if user_id in month_stats and month_stats[user_id] is not None:
                                    month_stats[user_id] += time_spent
                                else:
                                    month_stats[user_id] = time_spent

                    monthly_stats[target_month] = month_stats

            for target_month, month_stats in monthly_stats.items():
                month_name = datetime.date(1900, target_month, 1).strftime("%B")
                month_data = ""

                for user_id, time_spent in month_stats.items():
                    member = guild.get_member(user_id)
                    if member is None:
                        continue

                    if discord.utils.get(member.roles, id=role_id) is None:
                        continue

                    minutes, seconds = divmod(time_spent, 60)
                    hours, minutes = divmod(minutes, 60)

                    if hours >= 1:
                        month_data += f"**User: {member.display_name}**, Time: {int(hours)} hours.\n"

                if month_data:
                    em.add_field(name=f"{month_name}", value=month_data, inline=False)
                    em.set_footer(text=f"{month_name}")
                else:
                    em.add_field(name=f"{month_name}", value="No data available", inline=False)

            self.monthly_pages.append(em)

    def get_alltime_pages(self):
        return self.alltime_pages

    def get_weekly_pages(self):
        return self.weekly_pages

    def get_monthly_pages(self):
        return self.monthly_pages

    def get_pages(self):
        return self.pages

    skirastats = SlashCommandGroup("unitstats", "Shows all time stats for all users in x role with different commands"
                                                   "for different time scales.")


    @skirastats.command(name="alltime", description="Shows all time stats for all users in x role")
    async def alltime(self, ctx: discord.ApplicationContext, role: discord.Role):
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

