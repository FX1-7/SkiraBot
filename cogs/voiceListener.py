import discord
from discord.ext import commands
import time
import aiosqlite
from utils.utils import utc_now

time_start = {}


async def update_alltime_stats(db):
    day_number = int(utc_now().day)
    month_number = int(utc_now().month)
    await db.execute("UPDATE AllTimeStats SET TimeSpent = COALESCE((SELECT SUM(TimeSpent) FROM WeeklyStats "
                     "WHERE WeeklyStats.UserID = AllTimeStats.UserID AND WeeklyStats.ChannelID ="
                     " AllTimeStats.ChannelID), 0) + TimeSpent "
                     "WHERE EXISTS (SELECT 1 FROM WeeklyStats "
                     "WHERE WeeklyStats.UserID = AllTimeStats.UserID AND WeeklyStats.ChannelID ="
                     " AllTimeStats.ChannelID)")
    await db.commit()
    await db.execute("UPDATE LastUpdated SET Date=?, Month=?", (day_number, month_number))
    await db.commit()


async def move_data(db):
    weekly_cursor = await db.execute("SELECT * FROM WeeklyStats")
    all_time_cursor = await db.execute("SELECT * FROM AllTimeStats")

    async for weekly_row in weekly_cursor:
        user_id = weekly_row[0]
        channel_id = weekly_row[1]
        time_spent = weekly_row[2]
        time_spent = round(time_spent, 2)

        matching_row = await all_time_cursor.execute("SELECT * FROM AllTimeStats WHERE UserID = ? AND ChannelID = ?",
                                                     (user_id, channel_id))
        matching_row = await matching_row.fetchone()
        if matching_row:
            new_time_spent = matching_row[2] + time_spent
            new_time_spent = round(new_time_spent, 2)
            await db.execute("UPDATE AllTimeStats SET TimeSpent = ? WHERE UserID = ? AND ChannelID = ?",
                             (new_time_spent, user_id, channel_id))
            await db.commit()
        else:
            # Insert a new row with TimeSpent initialized to zero
            await db.execute("INSERT INTO AllTimeStats (UserID, ChannelID, TimeSpent) VALUES (?, ?, 0)",
                             (user_id, channel_id))
            await db.commit()

            # Retrieve the new row and update TimeSpent with the weekly time spent
            rows = await db.execute("SELECT * FROM AllTimeStats WHERE UserID = ? AND ChannelID = ?",
                                     (user_id, channel_id))
            new_row = await rows.fetchone()
            new_time_spent = new_row[2] + time_spent
            new_time_spent = round(new_time_spent, 2)
            await db.execute("UPDATE AllTimeStats SET TimeSpent = ? WHERE UserID = ? AND ChannelID = ?",
                             (new_time_spent, user_id, channel_id))
            await db.commit()
    await db.execute("DELETE FROM WeeklyStats")
    await db.commit()


async def db_conversion(db):
    if utc_now().day == 1:
        async with db.execute("SELECT Date, Month FROM LastUpdated") as last_date:
            last_date = await last_date.fetchall()
            for date in last_date:
                if date[0] == 1 and date[1] != utc_now().month:
                    await update_alltime_stats(db)
                    await move_data(db)


class VoiceListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channels = [] # List of all channels

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState):
        if before.channel != after.channel and after.channel:
            self.channels.append(after.channel.id)
            time_start[member.id] = time.time()
        if before.channel and before.channel.id in self.channels:
            duration = time.time() - time_start.get(member.id, 0)
            duration = round(duration, 2)
            async with aiosqlite.connect("data.db") as db:
                query = "SELECT * FROM WeeklyStats WHERE UserID=? AND ChannelID=?"
                rows = await db.execute(query, (member.id, before.channel.id))
                row = await rows.fetchone()
                if row:
                    # If there is a record in the db that matches the userID and current channel
                    time_spent = row[2] + duration
                    day_number = int(utc_now().day)
                    month_number = int(utc_now().month)
                    data = (time_spent, member.id, before.channel.id)
                    await db.execute("UPDATE WeeklyStats SET TimeSpent=? WHERE UserID=? AND ChannelID=?", data)
                    await db.commit()
                    await db_conversion(db)
                else:
                    # Record doesn't exist so create it
                    day_number = int(utc_now().day)
                    month_number = int(utc_now().month)
                    await db.execute("INSERT INTO WeeklyStats (UserID, ChannelID, TimeSpent) VALUES (?,?,?)",
                                     (member.id, before.channel.id, duration))
                    await db.commit()
                    async with db.execute("SELECT Date FROM LastUpdated") as last_date:
                        last_date = await last_date.fetchone()
                        if last_date is None:
                            await db.execute("INSERT INTO LastUpdated (Date, Month) VALUES (?, ?)", (day_number, month_number))
                            await db.commit()
                        else:
                            data = (member.id, before.channel.id)
                            rows = await db.execute("SELECT * FROM AllTimeStats WHERE UserID=? AND ChannelID=?", data)
                            row = await rows.fetchone()
                            if row:
                                # If there is a current record in the AllTime Table
                                time_spent = row[2] + duration
                                day_number = int(utc_now().day)
                                month_number = int(utc_now().month)
                                data = (time_spent, member.id, before.channel.id)
                                await db.execute("UPDATE AllTimeStats SET TimeSpent=? WHERE UserID=? AND ChannelID=?", data)
                                await db.commit()
                                await db_conversion(db)


def setup(bot):
    bot.add_cog(VoiceListener(bot))
