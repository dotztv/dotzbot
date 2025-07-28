# Setup
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
import discord
from discord.ext import commands
import secrets

print('bot.py executed at ', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def get_timenow():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def printlog(ctx):
    user = f"{ctx.author} ({ctx.author.id})"
    command = ctx.message.content
    location = ctx.guild.name if ctx.guild else "DMs"
    channel = f", {ctx.channel.name}" if ctx.guild else ""

    print(f"{user} used: '{command}' in {location}{channel} at {get_timenow()}")

def get_random_file(folder_path):
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    if not files:
        return None
    return os.path.join(folder_path, secrets.choice(files))

def get_uptime():
    now = datetime.utcnow()
    delta = now - bot_start_time
    days, remainder = divmod(delta.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', description="epic dotzbot", intents=intents, help_command=None)

bot_start_time = datetime.utcnow()

@bot.event
async def on_ready():
    startuptime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print('Time and date is ', startuptime)
    print(f'{bot.user} is ready and active!')
    embed = discord.Embed(
        title="dotzbot is online",
        description=startuptime,
        color=discord.Color.green()
    )
    dotzbotchannel = bot.get_channel(1399359500049190912)
    await dotzbotchannel.send(embed=embed)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.get_uptime = get_uptime
bot.printlog = printlog
bot.get_random_file = get_random_file
bot.bot_start_time = bot_start_time

bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)