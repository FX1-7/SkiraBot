import discord
from discord.ext import commands
from config import GUILD_ID
import aiosqlite


class Meta(commands.Cog):

    @commands.slash_command(guild_ids=[GUILD_ID], permissions=["manage_message"])
    async def purge(self, ctx, amount: int, error: discord.errors.NotFound):
        try:
            await ctx.defer()
            await ctx.channel.purge(limit=amount + 1)
            await ctx.respond(f"{ctx.author.mention}, you do not have permission to use that command.")
        except commands.MissingPermissions:
            await ctx.respond(f'{amount} Messages cleared by {ctx.author.mention}',
                              ephemeral=True)

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
