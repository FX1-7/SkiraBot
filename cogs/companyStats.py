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

                em = discord.Embed(title=f"🔊 Monthly Voice Stats - @{role} 🔊", colour=MAIN,
                                   timestamp=discord.utils.utcnow())

                for user_id, stats in user_stats.items():
                    total_time_spent = sum(stats.values())
                    minutes, seconds = divmod(total_time_spent, 60)
                    hours, minutes = divmod(minutes, 60)
                    days, hours = divmod(hours, 24)
                    days = round(days, 2)
                    hours = round(hours, 2)
                    minutes = round(minutes, 2)
                    seconds = round(seconds, 2)

                    user_name = self.bot.get_user(user_id)
                    time_string = ""
                    if days > 0:
                        time_string += f"{int(days)} days, "
                    if hours >= 1:
                        time_string += f"{int(hours)} hours."

                    if time_string:
                        em.add_field(name=f"User ID: {user_name.display_name}",
                                     value=f"**Total Play Time:** {time_string}", inline=False)

            self.alltime_pages.append(em)

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

                em = discord.Embed(title=f"🔊 Monthly Voice Stats - @{role} 🔊", colour=MAIN,
                                   timestamp=discord.utils.utcnow())

                for user_id, time_spent in user_stats.items():
                    minutes, seconds = divmod(time_spent, 60)
                    hours, minutes = divmod(minutes, 60)
                    days, hours = divmod(hours, 24)
                    days = round(days, 2)
                    hours = round(hours, 2)
                    minutes = round(minutes, 2)
                    seconds = round(seconds, 2)

                    user_name = self.bot.get_user(user_id)
                    time_string = ""
                    if days > 0:
                        time_string += f"{int(days)} days, "
                    if hours >= 1:
                        time_string += f"{int(hours)} hours."

                    if time_string:
                        em.add_field(
                            name=f"User ID: {user_name.display_name}",
                            value=f"Total Time Spent: {time_string}",inline=False)

                self.weekly_pages.append(em)

    async def monthlystats(self, role_id, guild_id):
        async with aiosqlite.connect("data.db") as db:
            guild = self.bot.get_guild(guild_id)
            role = guild.get_role(role_id)

            query = """
                SELECT UserID, SUM(TimeSpent) AS TotalTimeSpent
                FROM (
                    SELECT UserID, TimeSpent FROM WeeklyStats
                    UNION ALL
                    SELECT UserID, TimeSpent FROM MonthlyStats
                ) AS CombinedStats
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

                em = discord.Embed(title=f"🔊 Monthly Voice Stats - @{role} 🔊", colour=MAIN,
                                   timestamp=discord.utils.utcnow())

                for user_id, time_spent in user_stats.items():
                    minutes, seconds = divmod(time_spent, 60)
                    hours, minutes = divmod(minutes, 60)
                    days, hours = divmod(hours, 24)
                    days = round(days, 2)
                    hours = round(hours, 2)
                    minutes = round(minutes, 2)
                    seconds = round(seconds, 2)

                    user_name = self.bot.get_user(user_id)
                    time_string = ""
                    if days > 0:
                        time_string += f"{int(days)} days, "
                    if hours >= 1:
                        time_string += f"{int(hours)} hours."

                    if time_string:
                        em.add_field(
                            name=f"User ID: {user_name.display_name}", value=f"Total Time Spent:"
                                                                             f" {time_string}",inline=False)

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

