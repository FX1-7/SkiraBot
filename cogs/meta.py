import discord
from discord.ext import commands
from config import GUILD_ID
import aiosqlite


class Meta(commands.Cog):

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        """
        Purges messages.
        """
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f'{amount} Messages cleared by {ctx.author.mention}', delete_after=6)

    @commands.command()
    # @commands.has_role(KEIRAN_ID)
    async def querydb(self, ctx, *, query: str):
        async with aiosqlite.connect("data.db") as db:
            async with db.execute(query) as Data:
                entry = await Data.fetchall()
                for detail in entry:
                    await ctx.send(content=detail)

    @commands.command()
    async def dentry(self, ctx, table, *, userid: str):
        async with aiosqlite.connect("data.db") as db:
            if table == "m":
                await db.execute("DELETE FROM MonthlyStats Where UserID = ?", (userid,))
                await db.commit()
                await ctx.send(content="Deleted from Monthly")
            elif table == "w":
                await db.execute("DELETE FROM WeeklyStats Where UserID = ?", (userid,))
                await db.commit()
                await ctx.send(content="Deleted from Weekly")
            elif table == "a":
                await db.execute("DELETE FROM AllTimeStats Where UserID = ?", (userid,))
                await db.commit()
                await ctx.send(content="Deleted from AllTime")
            else:
                await ctx.send(content="Error!")


def setup(bot):
    bot.add_cog(Meta(bot))
