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
bot.activity_set = False

@bot.event
async def on_ready():
    if not bot.activity_set:
        activity = discord.Game(name="with your electric box :3")
        await bot.change_presence(activity=activity)
        bot.activity_set = True

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

# --- FUN COMMANDS ---

@bot.command(description="Get a random (unmoderated) meme")
async def meme(ctx):
    folder_path = "./memefolder"
    random_file = get_random_file(folder_path)
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    num_files = len(files)
    if random_file:
        filenaming = os.path.basename(random_file)
        embed = discord.Embed(
            title="Random Meme",
            description=filenaming,
            color=discord.Color.green()
        )
        embed.add_field(name="", value=f"{num_files} Files")
        embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
        await ctx.send(embed=embed)
        await ctx.send(file=discord.File(random_file))
    else:
        embed = discord.Embed(
            title="No Memes Found",
            description="Report to dotz",
            color=discord.Color.red()
        )
        embed.add_field(name="", value=f"{num_files} Files")
        embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
        await ctx.send(embed=embed)
    printlog(ctx)
    if random_file:
        print(f'{ctx.author} got the meme {filenaming}')
    else:
        print('ERROR: No meme found in the memefolder!')

@bot.command(description="Roll an X sided dice")
async def roll(ctx, dicesides: int = 100):
    if dicesides <= 0:
        embed = discord.Embed(
            title="Dice Roll",
            description=f"{ctx.author.mention} just tried to roll a {dicesides}-sided dice",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
        await ctx.send(embed=embed)
        printlog(ctx)
        print(f"{ctx.author} just tried to roll a {dicesides}-sided dice")
        return

    diceroll = 1 + secrets.randbelow(dicesides)
    embed = discord.Embed(
        title="Dice Roll",
        description=f"{ctx.author.mention} rolled a {dicesides}-sided dice and got {diceroll}",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
    await ctx.send(embed=embed)
    printlog(ctx)
    print(f'{ctx.author}\'s {dicesides}-sided dice landed on {diceroll}')

@bot.command(description="Flip a coin, Heads or tails?")
async def coinflip(ctx):
    coinsides = ["heads", "tails"]
    coin = secrets.choice(coinsides)
    embed = discord.Embed(
        title="Coin Flip",
        description=f"{ctx.author.mention} flipped a coin and it landed on {coin}",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
    await ctx.send(embed=embed)
    printlog(ctx)
    print(f'{ctx.author}\'s coin landed on {coin}')

@bot.command(description="Highest card wins")
async def highcard(ctx):
    usercard = 1 + secrets.randbelow(13)
    if usercard == 1:
        readableusercard = "Ace"
    elif usercard == 11:
        readableusercard = "Jack"
    elif usercard == 12:
        readableusercard = "Queen"
    elif usercard == 13:
        readableusercard = "King"
    else:
        readableusercard = str(usercard)

    botcard = 1 + secrets.randbelow(13)
    if botcard == 1:
        readablebotcard = "Ace"
    elif botcard == 11:
        readablebotcard = "Jack"
    elif botcard == 12:
        readablebotcard = "Queen"
    elif botcard == 13:
        readablebotcard = "King"
    else:
        readablebotcard = str(botcard)

    if usercard > botcard:
        winner = "user"
    elif usercard < botcard:
        winner = "bot"
    else:
        winner = "tie"
    if winner == "user":
        embed = discord.Embed(
            title="High Card Result",
            description=f"{ctx.author.mention} won with a {readableusercard} against {bot.user.mention}'s {readablebotcard}",
            color=discord.Color.green()
        )
        print(f'{ctx.author} wins! {ctx.author}\'s {readableusercard} vs {bot.user}\'s {readablebotcard}')
    elif winner == "bot":
        embed = discord.Embed(
            title="High Card Result",
            description=f"{bot.user.mention} won with a {readablebotcard} against {ctx.author.mention}'s {readableusercard}",
            color=discord.Color.red()
        )
        print(f'{bot.user} wins! {bot.user}\'s {readablebotcard} vs {ctx.author}\'s {readableusercard}')
    else:
        embed = discord.Embed(
            title="High Card Result",
            description=f"It's a tie! Both drew a {readableusercard}",
            color=discord.Color.grey()
        )
        print(f'{ctx.author} and {bot.user} tied with {readableusercard}')
    await ctx.send(embed=embed)
    printlog(ctx)

@bot.command(description="Play Rock Paper Scissors, default choice is scissors")
async def rps(ctx, choice: str = "scissors"):
    rpschoices = ["rock", "paper", "scissors"]
    userchoice = choice.lower()
    botchoice = secrets.choice(rpschoices)
    result = ""
    color = discord.Color.gold()

    if userchoice == botchoice:
        result = "It's a tie!"
        color = discord.Color.gold()
    elif (userchoice == "rock" and botchoice == "scissors") or \
         (userchoice == "scissors" and botchoice == "paper") or \
         (userchoice == "paper" and botchoice == "rock"):
        result = f"{ctx.author.mention} wins!"
        color = discord.Color.green()
    elif (botchoice == "rock" and userchoice == "scissors") or \
         (botchoice == "scissors" and userchoice == "paper") or \
         (botchoice == "paper" and userchoice == "rock"):
        result = f"{bot.user.mention} wins!"
        color = discord.Color.red()
    else:
        result = "Invalid choice! Please choose rock, paper, or scissors."
        color = discord.Color.red()

    embed = discord.Embed(
        title="Rock Paper Scissors",
        description=(
            f"{ctx.author.mention} chose **{userchoice.capitalize()}**\n"
            f"{bot.user.mention} chose **{botchoice.capitalize()}**\n\n"
            f"{result}"
        ),
        color=color
    )
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
    await ctx.send(embed=embed)
    printlog(ctx)
    if result == f"{ctx.author.mention} wins!":
        print(f"{ctx.author} wins! {ctx.author}'s {userchoice} vs {bot.user}'s {botchoice}")
    elif result == f"{bot.user.mention} wins!":
        print(f"{bot.user} wins! {bot.user}'s {botchoice} vs {ctx.author}'s {userchoice}")
    elif result == "It's a tie!":
        print(f"{ctx.author} tied against {bot.user} in RPS")
    else:
        print(f'ERROR: Error in {ctx.message.content}! Executed by {ctx.author} ({ctx.author.id}) at {get_timenow()}')

# --- INFO COMMANDS ---

@bot.command(description="Shows this list!")
async def help(ctx):
    embed = discord.Embed(
        title="dotzbot commands",
        description="",
        color=discord.Color.gold()
    )
    for command in bot.commands:
        embed.add_field(
            name=f"${command.name}",
            value=command.description or "No description.",
            inline=False
        )
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
    await ctx.send(embed=embed)
    printlog(ctx)

@bot.command(description="Show the bot's latency")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="Pong!",
        description=f"Latency: {latency} ms",
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)
    printlog(ctx)
    print(f'Reported Latency: {latency}')

@bot.command(description="Show how long the bot has been running")
async def uptime(ctx):
    uptime_str = get_uptime()
    embed = discord.Embed(
        title="Uptime",
        description=f"The bot has been running for: {uptime_str}",
        color=discord.Color.gold()
    )
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
    await ctx.send(embed=embed)
    printlog(ctx)
    print(f'Bot Uptime: {uptime_str}')

@bot.command(description="General info about the bot")
async def botinfo(ctx):
    # You can expand this with more info if you want
    await ctx.send("Command still in the works, so no info for you yet")
    printlog(ctx)

@bot.command(description="Get info about a UserID")
async def userinfo(ctx, userid: int = 1267637358942224516):
    user = await bot.fetch_user(userid)
    member = ctx.guild.get_member(userid) if ctx.guild else None
    target = member if member else user

    if userid == 550378971426979856:
        description = "Hey, It's my creator!"
    elif userid == 1267637358942224516:
        description = "Wait a minute, that's me!"
    else:
        description = ""

    embed = discord.Embed(
        title="User Information",
        description=description,
        color=discord.Color.green()
    )
    embed.add_field(name="Username", value=target.name)
    embed.add_field(name="User ID", value=str(target.id))
    embed.add_field(name="Account Created", value=target.created_at.strftime('%Y-%m-%d %H:%M:%S'))
    embed.add_field(name="Bot?", value="Yes" if target.bot else "No")
    if member and member.joined_at:
        embed.add_field(name="Joined Server", value=member.joined_at.strftime('%Y-%m-%d %H:%M:%S'))
    if member and member.roles:
        embed.add_field(
            name="Roles",
            value=", ".join([role.name for role in member.roles if role.name != "@everyone"])
        )
    if target.avatar:
        embed.set_thumbnail(url=target.avatar.url)
    if hasattr(user, "banner") and user.banner:
        embed.set_image(url=user.banner.url)
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
    await ctx.send(embed=embed)
    printlog(ctx)

@bot.command(description="Get info about the current server")
async def serverinfo(ctx):
    if ctx.guild:
        servername = ctx.guild.name
        embeddesc = ""
        embedcolor = discord.Color.green()
    else:
        servername = "This is a DM"
        embeddesc = "But I'll try to give you some information anyways"
        embedcolor = discord.Color.gold()

    embed = discord.Embed(
        title=servername,
        description=embeddesc,
        color=embedcolor
    )
    if ctx.guild:
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        if ctx.guild.description:
            embed.add_field(name="Server Description", value=str(ctx.guild.description), inline=False)
        embed.add_field(name="Server ID", value=str(ctx.guild.id), inline=True)
        embed.add_field(name="Server Creation Date", value=ctx.guild.created_at.strftime('%Y-%m-%d %H:%M:%S'), inline=True)
        embed.add_field(name="Server Member Count", value=str(ctx.guild.member_count), inline=True)
        embed.add_field(name="Server Owner", value=str(ctx.guild.owner), inline=True)
        embed.add_field(name="Verification Level", value=str(ctx.guild.verification_level), inline=True)
        embed.add_field(name="AFK Channel", value=str(ctx.guild.afk_channel), inline=True)
        embed.add_field(name="AFK Timeout", value=str(ctx.guild.afk_timeout), inline=True)
        embed.add_field(name="Server Boosts", value=str(ctx.guild.premium_subscription_count), inline=True)
        embed.add_field(name="Server Features", value=str(ctx.guild.features), inline=False)
    else:
        embed.add_field(name="Channel ID", value=str(ctx.channel.id), inline=True)
        embed.add_field(name="Channel Creation Date", value=ctx.channel.created_at.strftime('%Y-%m-%d %H:%M:%S'), inline=True)
        embed.add_field(name="Channel Type", value=str(ctx.channel.type), inline=True)
        embed.add_field(name="Your Username", value=ctx.author.name, inline=True)
        embed.add_field(name="Your User ID", value=str(ctx.author.id), inline=True)
        embed.add_field(name="Your Account Created", value=ctx.author.created_at.strftime('%Y-%m-%d %H:%M:%S'), inline=True)
        embed.add_field(name="Are you a bot?", value="Yes" if ctx.author.bot else "No", inline=True)
        if ctx.author.avatar:
            embed.set_thumbnail(url=ctx.author.avatar.url)

    await ctx.send(embed=embed)
    printlog(ctx)

# --- ADMIN COMMANDS ---

@bot.command(description="Shuts down the bot (dotz only)")
@commands.is_owner()
async def shutdown(ctx):
    timeatshutdown = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    embed = discord.Embed(
        title="dotzbot is offline",
        description=timeatshutdown,
        color=discord.Color.red()
    )
    embed.add_field(name="", value=f"Uptime: {get_uptime()}")
    dotzbotchannel = bot.get_channel(1399359500049190912)
    emoji = '✅'
    await ctx.message.add_reaction(emoji)
    await dotzbotchannel.send(embed=embed)
    print(f'Time is {timeatshutdown}')
    await bot.close()

@bot.command(description="List all servers the bot is in (dotz only)")
@commands.is_owner()
async def serverlist(ctx):
    guilds = bot.guilds
    embed = discord.Embed(
        title="Server List",
        description=f"The bot is in {len(guilds)} servers:",
        color=discord.Color.gold()
    )
    for guild in guilds:
        embed.add_field(
            name=guild.name,
            value=f"ID: {guild.id} | Members: {guild.member_count}",
            inline=False
        )
    await ctx.send(embed=embed)

bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)