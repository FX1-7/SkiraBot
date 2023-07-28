import discord
from discord.ext import commands
import os
from os import getenv
from dotenv import load_dotenv
from config import LOG_ID, PREFIX, OWNERS

load_dotenv()


class Bot(commands.Bot):
    async def on_ready(self):
        # Print startup message
        startup = bot.user.name + " is running"
        print(startup)
        print("-" * len(startup))  # Print a line of dashes as long as the last print line for neatness

        channel = self.get_channel(LOG_ID)
        await channel.send(f"<@114352655857483782> - restart detected.")


intents = discord.Intents.all()
bot = Bot(command_prefix=commands.when_mentioned_or(PREFIX), messages=True, case_insensitive=True, owner_ids=OWNERS,
          allowed_mentions=discord.AllowedMentions(roles=False, everyone=False), intents=intents)

# Load cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        print("Loading: cogs." + filename[:-3])
        bot.load_extension("cogs." + filename[:-3])

# Start the bot
bot.run(getenv("BOT_TOKEN"))
