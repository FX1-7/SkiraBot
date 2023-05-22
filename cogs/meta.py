import discord
from discord.ext import commands
from config import GUILD_ID
import aiosqlite
from voiceListener import move_data_to_monthly


class Meta(commands.Cog):

    @discord.slash_command(guild_ids=[GUILD_ID])
    async def purge(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount+1)
        await ctx.respond(f'{amount} Messages cleared by {ctx.author.mention}',
                          ephemeral=True)

    @commands.command()
    async def querydb(self, ctx, *, query: str):
        async with aiosqlite.connect("data.db") as db:
            async with db.execute(query) as Data:
                entry = await Data.fetchall()
                for detail in entry:
                    await ctx.send(content=detail)

def setup(bot):
    bot.add_cog(Meta(bot))
