import discord
from discord.ext import commands
from jishaku.help_command import MinimalEmbedPaginatorHelp
from config import GUILD_ID


class Meta(commands.Cog):

    @discord.slash_command(guild_ids=[GUILD_ID])
    async def purge(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount+1)
        await ctx.respond(f'{amount} Messages cleared by {ctx.author.mention}',
                          ephemeral=True)


def setup(bot):
    bot.add_cog(Meta(bot))
