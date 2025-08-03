# --- Imports ---
import logging
import os
from datetime import datetime

from dotenv import load_dotenv
import discord
from discord.ext import commands
import secrets

# --- Functions ---


def get_time_now() -> str:
    """Returns current (local) time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_random_file(folder_path) -> str:
    """Returns a random file."""
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    return os.path.join(folder_path, secrets.choice(files))


def get_uptime() -> str:
    """Returns the bot's uptime."""
    now = datetime.utcnow()
    delta = now - BOT_START_TIME
    days, remainder = divmod(delta.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"


# --- Setup ---

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN") # Gets the discord token from the .env file
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w') # Sets up logging
intents = discord.Intents.all() # Gives it all intents, TODO: Make it only have what it needs, same with permissions
bot = commands.Bot(command_prefix="$", intents=intents, help_command=None) # Sets up bot with discord.ext command prefix, all intents and removes default help command


bot.activity_set = False


# --- Bot Events ---

@bot.event
async def on_ready():
    if not bot.activity_set: # Makes it do it only once
        activity = discord.Game(name="with your electric box :3") # Sets Activity to: Playing with your electric box :3
        await bot.change_presence(activity=activity)
        bot.activity_set = True

    global BOT_START_TIME # makes sure it's usable everywhere
    BOT_START_TIME = datetime.utcnow() # also used in get_uptime()

    embed = discord.Embed(
        title="dotzbot is online",
        description=BOT_START_TIME,
        color=discord.Color.green()
    )
    dotzbot_channel = bot.get_channel(1399359500049190912) # Channel ID of my server's channel for the bot
    await dotzbot_channel.send(embed=embed) # Sends it to the specified channel


@bot.event # Vibe coded error handler
async def on_command_error(ctx, error):
    embed = discord.Embed(
        title="An error occurred",
        description=f"{type(error).__name__}: {error}",
        color=discord.Color.red()
    )
    await ctx.reply(embed=embed, mention_author=True)


# --- FUN COMMANDS ---


@bot.command(description="Get a random (un-moderated) meme")
async def meme(ctx):
    folder_path = "./memefolder"
    random_file = get_random_file(folder_path)
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))] # Gets all the files in folder_path, needed to count all files
    num_files = len(files)
    file_name = os.path.basename(random_file)

    embed = discord.Embed(
        title="Random Meme",
        description=file_name,
        color=discord.Color.green()
    )
    embed.add_field(name="", value=f"{num_files} Files")
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")

    await ctx.reply(embed=embed, file=discord.File(random_file), mention_author=True)


@bot.command(description="Roll an X sided dice", aliases=["dice", "dice_roll", "diceroll", "rolldice", "roll_dice"])
async def roll(ctx, dice_sides: int = 100):
    if dice_sides <= 0: # If equal or less
        embed = discord.Embed(
            title="Dice Roll",
            description=f"{ctx.author.mention} just tried to roll a {dice_sides}-sided dice",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
        await ctx.reply(embed=embed, mention_author=True)

        return # to not continue code

    dice_roll = 1 + secrets.randbelow(dice_sides)
    embed = discord.Embed(
        title="Dice Roll",
        description=f"{ctx.author.mention} rolled a {dice_sides}-sided dice and got {dice_roll}",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
    await ctx.reply(embed=embed, mention_author=True)


@bot.command(description="Flip a coin, Heads or tails?", aliases=["cf", "coin", "flip", "flipacoin"])
async def coinflip(ctx):
    coin_sides = ["heads", "tails"]
    coin = secrets.choice(coin_sides)
    embed = discord.Embed(
        title="Coin Flip",
        description=f"{ctx.author.mention} flipped a coin and it landed on {coin}",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
    await ctx.reply(embed=embed, mention_author=True)


@bot.command(description="Highest card wins", aliases=["hc"])
async def highcard(ctx):
    user_card = 1 + secrets.randbelow(13)

    if user_card == 1:
        user_card = 14
        readable_user_card = "Ace"
    elif user_card == 11:
        readable_user_card = "Jack"
    elif user_card == 12:
        readable_user_card = "Queen"
    elif user_card == 13:
        readable_user_card = "King"

    bot_card = 1 + secrets.randbelow(13)
    if bot_card == 1:
        bot_card = 14
        readable_bot_card = "Ace"
    elif bot_card == 11:
        readable_bot_card = "Jack"
    elif bot_card == 12:
        readable_bot_card = "Queen"
    elif bot_card == 13:
        readable_bot_card = "King"

    if user_card > bot_card: # If user wins
        embeddesc = f"{ctx.author.mention} won with a {readable_user_card} against {bot.user.mention}'s {readable_bot_card}"
        embedcolor = discord.Color.green()
    elif bot_card > user_card: # or bot wins
        embeddesc = f"{bot.user.mention} won with a {readable_bot_card} against {ctx.author.mention}'s {readable_user_card}"
        embedcolor = discord.Color.red()
    else: # or it's a tie
        embeddesc = f"It's a tie! Both drew a {readable_user_card}"
        embedcolor = discord.Color.yellow()


    embed = discord.Embed(
        title="High Card Result",
        description=embeddesc,
        color=embedcolor
    )
    await ctx.reply(embed=embed, mention_author=True)


@bot.command(description="Play Rock Paper Scissors, default choice is scissors")
async def rps(ctx, choice: str = "scissors"):
    rps_choices = ["rock", "paper", "scissors"]
    user_choice = choice.lower() # make the input/argument lowercase
    bot_choice = secrets.choice(rps_choices)
    color = discord.Color.gold()

    if user_choice == bot_choice:
        result = "It's a tie!"
        color = discord.Color.gold()
    elif (user_choice == "rock" and bot_choice == "scissors") or \
         (user_choice == "scissors" and bot_choice == "paper") or \
         (user_choice == "paper" and bot_choice == "rock"):
        result = f"{ctx.author.mention} wins!" # user wins
        color = discord.Color.green()
    elif (bot_choice == "rock" and user_choice == "scissors") or \
         (bot_choice == "scissors" and user_choice == "paper") or \
         (bot_choice == "paper" and user_choice == "rock"):
        result = f"{bot.user.mention} wins!" # bot wins
        color = discord.Color.red()
    else:
        result = "Invalid choice! Please choose rock, paper, or scissors."
        color = discord.Color.red()

    embed = discord.Embed(
        title="Rock Paper Scissors",
        description=(
            f"{ctx.author.mention} chose **{user_choice.capitalize()}**\n" # New Lines for style
            f"{bot.user.mention} chose **{bot_choice.capitalize()}**\n\n"
            f"{result}"
        ),
        color=color
    )
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
    await ctx.reply(embed=embed, mention_author=True)


@bot.command(description="The wisdom of the eight ball upon you", aliases=["8ball", "8b"])
async def eightball(ctx):
    yes_answers = [ # 7
        "yes", "why not", "absolutely", "hell yeah", "without a doubt", "absolutely", "uh, obviously"
    ]
    no_answers = [ # 7
        "no", "absolutely not", "fuck no", "nah", "are you stupid? no", "nuh uh", "not happening"
    ]
    unknown_answers = [ # 7
        "i'm not too sure", "i don't know", "the answer lies in the question itself",
        "the answer can be found in your soul", "do what your heart desires", "whatever you feel like",
        "idk, ask the next guy"
    ]

    eight_ball_answers = ["yes", "no", "unknown"] # makes it equal chance for yes, no or unknown incase there are different amounts of strings in each list
    eight_ball_first_choice = secrets.choice(eight_ball_answers)

    if eight_ball_first_choice == "yes":
        eight_ball_real_choice = secrets.choice(yes_answers)
        embed_color = discord.Color.green()
    if eight_ball_first_choice == "no":
        eight_ball_real_choice = secrets.choice(no_answers)
        embed_color = discord.Color.red()
    if eight_ball_first_choice == "unknown":
        eight_ball_real_choice = secrets.choice(unknown_answers)
        embed_color = discord.Color.yellow()

    embed = discord.Embed(
        title="8 ball's answer",
        description=f"The 8 ball says: {eight_ball_real_choice}",
        color=embed_color
    )

    await ctx.reply(embed=embed, mention_author=True)


# --- INFO COMMANDS ---


@bot.command(description="Shows this list!", aliases=["?"])
async def help(ctx):
    is_owner = False
    try:
        is_owner = await bot.is_owner(ctx.author)
    except (discord.HTTPException, discord.Forbidden, discord.NotFound): # Connection Failed (API Unreachable / Network Issue), No Permission or User doesn't exist
        pass

    embed = discord.Embed(
        title="dotzbot's commands",
        description="",
        color=discord.Color.gold()
    )
    for command in bot.commands:
        if command.hidden and not is_owner:
            continue # Somehow(vibe coded) shows hidden commands for bot owner
        embed.add_field(
            name=f"${command.name}",
            value=command.description or "No description.",
            inline=False
        )
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
    await ctx.reply(embed=embed, mention_author=True)


@bot.command(description="Show the bot's latency", aliases=["latency", "lag", "ms"])
async def ping(ctx):
    latency = round(bot.latency * 1000) # Copilot told me to multiply this by a thousand so
    embed = discord.Embed(
        title="Pong!",
        description=f"Latency: {latency} ms",
        color=discord.Color.gold()
    )
    await ctx.reply(embed=embed, mention_author=True)


@bot.command(description="Show how long the bot has been running", aliases=["lifetime", "upkeep"])
async def uptime(ctx):
    uptime_str = get_uptime()
    embed = discord.Embed(
        title="dotzbot's Uptime",
        description=f"The bot has been running for: {uptime_str}",
        color=discord.Color.gold()
    )
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
    await ctx.reply(embed=embed, mention_author=True)


@bot.command(description="General info about the bot", aliases=["bot", "about"])
async def botinfo(ctx):
    await ctx.reply("Command still in the works, so no info for you yet", mention_author=True)


@bot.command(description="Get info about a UserID", aliases=["user", "checkuser"])
async def userinfo(ctx, userid: int = 1267637358942224516): # Defaults to dotzbot UserID
    user = await bot.fetch_user(userid)
    member_obj = ctx.guild.get_member(userid) if ctx.guild else None
    target_user = member_obj if member_obj else user

    if userid == 550378971426979856: # dotz
        description = "Hey, It's my creator!"
    elif userid == 1267637358942224516: # dotzbot
        description = "Wait a minute, that's me!"
    else:
        description = ""

    embed = discord.Embed(
        title="User Information",
        description=description,
        color=discord.Color.green()
    )
    embed.add_field(name="Username", value=target_user.name)
    embed.add_field(name="User ID", value=str(target_user.id))
    embed.add_field(name="Account Created", value=target_user.created_at.strftime("%Y-%m-%d %H:%M:%S"))
    embed.add_field(name="Bot?", value="Yes" if target_user.bot else "No")

    if member_obj and member_obj.joined_at: # If run in a server
        embed.add_field(name="Joined Server", value=member_obj.joined_at.strftime("%Y-%m-%d %H:%M:%S"))
    if member_obj and member_obj.roles: # If run in a server, for some reason will still run even if user has no roles
        embed.add_field(
            name="Roles",
            value=", ".join([role.name for role in member_obj.roles if role.name != "@everyone"])
        )
    if target_user.avatar:
        embed.set_thumbnail(url=target_user.avatar.url) # Sets user's pfp as thumbnail (small, top right)
    if hasattr(user, "banner") and user.banner:
        embed.set_image(url=user.banner.url) # Sets user's banner (Nitro Feature) as image (big, underneath)
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
    await ctx.reply(embed=embed, mention_author=True)


@bot.command(description="Get info about the current server", aliases=["server", "checkserver"])
async def serverinfo(ctx):
    if ctx.guild: # if run in a server
        server_name = ctx.guild.name
        embed_desc = ""
        embed_color = discord.Color.green()
    else: # if not run a in a server, therefore DM
        server_name = "This is a DM"
        embed_desc = "But I'll try to give you some information anyways"
        embed_color = discord.Color.gold()

    embed = discord.Embed(
        title=server_name,
        description=embed_desc,
        color=embed_color
    )

    if ctx.guild: # If run in a server
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        if ctx.guild.description:
            embed.add_field(name="Server Description", value=str(ctx.guild.description), inline=False)
        embed.add_field(name="Server ID", value=str(ctx.guild.id), inline=True)
        embed.add_field(name="Server Creation Date", value=ctx.guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="Server Member Count", value=str(ctx.guild.member_count), inline=True)
        embed.add_field(name="Server Owner", value=str(ctx.guild.owner), inline=True)
        embed.add_field(name="Verification Level", value=str(ctx.guild.verification_level), inline=True)
        embed.add_field(name="AFK Channel", value=str(ctx.guild.afk_channel), inline=True)
        embed.add_field(name="AFK Timeout", value=str(ctx.guild.afk_timeout), inline=True)
        embed.add_field(name="Server Boosts", value=str(ctx.guild.premium_subscription_count), inline=True)
        embed.add_field(name="Server Features", value=str(ctx.guild.features), inline=False)
    else: # If not run in a server, therefore DM
        embed.add_field(name="Channel ID", value=str(ctx.channel.id), inline=True)
        embed.add_field(name="Channel Creation Date", value=ctx.channel.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="Channel Type", value=str(ctx.channel.type), inline=True)
        embed.add_field(name="Your Username", value=ctx.author.name, inline=True)
        embed.add_field(name="Your User ID", value=str(ctx.author.id), inline=True)
        embed.add_field(name="Your Account Created", value=ctx.author.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="Are you a bot?", value="Yes" if ctx.author.bot else "No", inline=True)
        if ctx.author.avatar:
            embed.set_thumbnail(url=ctx.author.avatar.url) # Sets user's pfp as thumbnail (small, top right)

    await ctx.reply(embed=embed, mention_author=True)


# --- MODERATION COMMANDS ---


# --- ADMIN COMMANDS ---


@bot.command(description="Shuts down the bot (dotz only)", hidden=True, aliases=["die", "kys", "fuckingdie", "de-exist"])
@commands.is_owner()
async def shutdown(ctx):
    time_at_shutdown = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    embed = discord.Embed(
        title="dotzbot is offline",
        description=time_at_shutdown,
        color=discord.Color.red()
    )
    embed.add_field(name="", value=f"Uptime: {get_uptime()}")
    dotzbot_channel = bot.get_channel(1399359500049190912)
    emoji = "✅" # defines emoji to react with
    await ctx.message.add_reaction(emoji)
    await dotzbot_channel.send(embed=embed)
    await bot.close()


@bot.command(description="List all servers the bot is in (dotz only)", hidden=True, aliases=["servers"])
@commands.is_owner()
async def serverlist(ctx):
    guild_list = bot.guilds
    embed = discord.Embed(
        title="Server List",
        description=f"The bot is in {len(guild_list)} servers:",
        color=discord.Color.gold()
    )
    for guild in guild_list: # Adds each guild as it's own field
        embed.add_field(
            name=guild.name,
            value=f"ID: {guild.id} | Members: {guild.member_count}",
            inline=False
        )
    await ctx.reply(embed=embed, mention_author=True)

bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)