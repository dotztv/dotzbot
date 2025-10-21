# --- Imports ---


# Standard library
import json
import logging
import os
import platform
import secrets
from datetime import datetime, time
from zoneinfo import ZoneInfo

# Third-party
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands, tasks
import requests
from dotenv import load_dotenv
from ossapi import Ossapi  # temporary, for a osu!pp war between friends


# --- Functions ---


def get_time_now() -> str:
    """Returns current (local) time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_uptime() -> str:
    """Returns the bot's uptime."""
    now = datetime.now(CESTIME)
    delta = now - BOT_START_TIME
    days, remainder = divmod(delta.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"


def get_command_count(bot): # Partly made by chatgpt
    visible = len([cmd for cmd in bot.commands if not cmd.hidden])
    hidden = len([cmd for cmd in bot.commands if cmd.hidden])
    return visible, hidden


# --- Setup ---


load_dotenv()
intents = discord.Intents.all()  # Gives it all intents, TODO: Make it only have what it needs, same with permissions
bot = commands.Bot(command_prefix="$", intents=intents, help_command=None)  # Sets up bot with discord.ext command prefix, all intents and removes default help command

LOUU_DM = os.getenv("LOUU_DM")  # for privacy reasons
CESTIME = ZoneInfo("Europe/Oslo")  # should definetely name that better

TOKEN = os.getenv("DISCORD_TOKEN")  # Gets the discord token from the .env file
BOT_START_TIME = datetime.now(CESTIME)

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")  # Sets up logging
logging.basicConfig(format=f"%(asctime)s / %(levelname)s = %(message)s", level=logging.INFO)

# osu!pp war - temporary
OSSAPI_SECRET = os.getenv("OSUAPI-SECRET")
OSSAPI_CLIENT_ID = os.getenv("OSUAPI-CLIENT-ID")
SINDRUS_DM = os.getenv("SINDRUS_DM")  # for privacy reasons


# --- Bot Events ---


@bot.event
async def on_ready():
    embed = discord.Embed(
        title="dotzbot is online",
        description=BOT_START_TIME.strftime("%Y-%m-%d %H:%M:%S"),  # Formats to a more readable version
        color=discord.Color.green()
    )
    dotzbot_channel = bot.get_channel(1399359500049190912)  # Channel ID of my server's channel for the bot
    await dotzbot_channel.send(embed=embed)  # Sends it to the specified channel
    logging.info(f"Logged in as {bot.user}")
    # Sync application commands: first to dev guild for fast testing, then globally
    try:
        dev_guild = discord.Object(id=907012194175176714)
        await bot.tree.sync(guild=dev_guild)
        logging.info(f"Synced application commands to dev guild {dev_guild.id}")
    except Exception:
        logging.exception("Failed to sync application commands to dev guild")

    # Global sync moved to owner-only command ($synctree)
    if not random_activity.is_running():  # Incase we disconnect, it'll fire this again.
        random_activity.start()  # If it's already running, it'll raise an error.
    if not dm_louu.is_running():
        dm_louu.start()
    if not osupp_war.is_running():
        osupp_war.start()


@bot.event # Vibe coded error handler
async def on_command_error(ctx, error):
    embed = discord.Embed(
        title="An error occurred",
        description=f"{type(error).__name__}: {error}",
        color=discord.Color.red()
    )
    await ctx.reply(embed=embed, mention_author=True)
    logging.error(f"{error}")


@bot.event
async def on_guild_join(guild):
    allowedservers = [1303080585216131082, 1345174170572554362, 907012194175176714]
    """Allowed Servers: (in order)
    dotz's corner
    gamers inc. (reincarnated)
    .PlaySpace
    """

    owner = guild.owner or await bot.fetch_user(guild.owner_id)

    if guild.id in allowedservers:
        pass
    else:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(f"Sorry {owner.mention}, This server isn't apart of dotz's allowed server list. Contact dotz for help.")
                logging.info(f"Left disallowed server, {guild.name} ({guild.id})")
                break
        await guild.leave()


# --- TASKS ---


@tasks.loop(seconds=300)  # 5min / 288 times per 24 hours
async def random_activity():
    activity_types = ["playing", "watching", "streaming", "listening to"]
    real_activity_type = secrets.choice(activity_types)

    playing_activities = [
        "with your electric box",
        "with the doll in my basement",
        "with dotz's sanity",
    "with my balls"  # by sindre6190
    ]

    watching_activities = [
        "you",
        "over everything you say",
        "the drama"
    ]

    streaming_activities = [
        "your webcam",
        "your browser history",
        "the hidden camera in your room",
        "your fridge"
    ]

    listening_activities = [
        "the voices in my head",
        "the drama",
        "the silence",
        "how useless i am",
    ]

    if real_activity_type == "playing":
        chosen_activity = secrets.choice(playing_activities)
        activity = discord.Game(name=chosen_activity)
    elif real_activity_type == "watching":
        chosen_activity = secrets.choice(watching_activities)
        activity = discord.Activity(name=chosen_activity, type=discord.ActivityType.watching)
    elif real_activity_type == "streaming":
        chosen_activity = secrets.choice(streaming_activities)
        activity = discord.Streaming(name=chosen_activity, type=discord.ActivityType.streaming, url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")  # may or may not be a rick roll
    elif real_activity_type == "listening to":
        chosen_activity = secrets.choice(listening_activities)
        activity = discord.Activity(name=chosen_activity, type=discord.ActivityType.listening)

    await bot.change_presence(activity=activity)
    logging.info(f"Activity: {real_activity_type} {chosen_activity}")


@random_activity.before_loop
async def before_loop():
    await bot.wait_until_ready()
    logging.info("Started random_activity")


@tasks.loop(time=time(hour=0, minute=30, tzinfo=CESTIME))
async def dm_louu():
    try:
        user = bot.get_user(int(LOUU_DM))
        await user.send("Reminder to do your QOTD!")
    except Exception as error:
        logging.error(f"dm_louu failed: {error}")

    logging.info("Reminded louuheyy for QOTD")


@dm_louu.before_loop
async def before_dmlouu():
    await bot.wait_until_ready()
    logging.info("Started dm_louu")


@tasks.loop(time=time(hour=16, minute=30, tzinfo=CESTIME))  # ossapi usage
async def osupp_war():
    api = Ossapi(client_id=OSSAPI_CLIENT_ID, client_secret=OSSAPI_SECRET)
    
    sindrusumulius = api.user("sindrusumulius")
    louuheyy = api.user("louuheyy")

    sindrusPP = sindrusumulius.statistics.pp
    louuPP = louuheyy.statistics.pp

    if sindrusPP > louuPP:
        leader = "sindrusumulius"
        pp_lead = sindrusPP - louuPP
    elif sindrusPP < louuPP:
        leader = "louuheyy"
        pp_lead = louuPP - sindrusPP
    else:
        leader = "Perfect Tie"
        pp_lead = 0
    
    embed = discord.Embed(
        title="osu!pp war report",
        description=get_time_now(),
        color=discord.Color.green()
    )
    embed.add_field(name="", value=f"sindrusumulius: **{sindrusPP:.3f}**pp")
    embed.add_field(name="", value=f"louuheyy: **{louuPP:.3f}**pp")
    embed.add_field(name="", value=f"Lead: **{pp_lead:.3f}pp** to **{leader}**")
    embed.set_footer(text="why did i do this -dotz")

    try:
        louuuser = bot.get_user(int(LOUU_DM))
        sindrususer = bot.get_user(int(SINDRUS_DM))
        dotzuser = bot.get_user(550378971426979856)
        if louuuser:
            await louuuser.send(embed=embed)
        if sindrususer:
            await sindrususer.send(embed=embed)
        if dotzuser:
            await dotzuser.send(embed=embed)
    except Exception as error:
        logging.error(f"osupp_war failed: {error}")
    

# --- FUN COMMANDS ---


@bot.hybrid_command(with_app_command=True, description="Get a random meme", aliases=["memes"])
async def meme(ctx):
    response = requests.get("https://meme-api.com/gimme")  # these first two lines are stolen
    json_data = json.loads(response.text)  # from a codedex guide of how to make a discord bot
    
    name = json_data["title"]
    subreddit = json_data["subreddit"]
    url = json_data["url"]
    nsfw = json_data["nsfw"]

    if str(nsfw).lower() == "true":
        embed = discord.Embed(
            title="Failed to get a meme",
            description="Please try again",
            color=discord.Color.red()
        )
        embed.add_field(name="Error", value="The meme fetched was marked as NSFW, and dotz is too lazy to make it redo the thing")
        embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
        await ctx.reply(embed=embed, mention_author=True)
        logging.info(f"{ctx.author} ({ctx.author.id}) got an NSFW meme, blocked")
        return

    async with aiohttp.ClientSession() as session:  # this thing is 99% stolen from whatever ai the google search engine has
        async with session.get(url) as resp:
            if resp.status == 200:
                with open("meme.png", "wb") as f:
                    f.write(await resp.read())

    embed = discord.Embed(
        title=name,
        description=f"r/{subreddit}",
        color=discord.Color.green()
    )
    embed.add_field(name="API", value="https://meme-api.com/gimme")
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
    await ctx.reply(embed=embed, file=discord.File("meme.png"), mention_author=True)
meme.category = "fun"


@bot.hybrid_command(with_app_command=True, description="Roll an X sided dice", aliases=["dice", "dice_roll", "diceroll", "rolldice", "roll_dice"])
async def roll(ctx, dice_sides: int = 100):
    if dice_sides <= 0:  # If equal or less
        embed = discord.Embed(
            title="Dice Roll",
            description=f"{ctx.author.mention} just tried to roll a {dice_sides}-sided dice",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
        await ctx.reply(embed=embed, mention_author=True)
        
        logging.info(f"{ctx.author} ({ctx.author.id}) just tried to roll a {dice_sides}-sided dice")
        return  # to not continue code

    dice_roll = 1 + secrets.randbelow(dice_sides)
    embed = discord.Embed(
        title="Dice Roll",
        description=f"{ctx.author.mention} rolled a {dice_sides}-sided dice and got {dice_roll}",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
    await ctx.reply(embed=embed, mention_author=True)
    logging.info(f"{ctx.author} ({ctx.author.id}) rolled a {dice_sides}-sided dice and got {dice_roll}")
roll.category = "fun"


@bot.hybrid_command(with_app_command=True, description="Flip a coin, Heads or tails?", aliases=["cf", "coin", "flip", "flipacoin"])
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
    logging.info(f"{ctx.author}'s ({ctx.author.id}) coin landed on {coin}")
coinflip.category = "fun"


@bot.hybrid_command(with_app_command=True, description="Highest card wins", aliases=["hc"])
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
    else:
        readable_user_card = user_card

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
    else:
        readable_bot_card = bot_card

    if user_card > bot_card:  # If user wins
        embeddesc = f"{ctx.author.mention} won with a {readable_user_card} against {bot.user.mention}'s {readable_bot_card}"
        embedcolor = discord.Color.green()
        logging.info(f"{ctx.author} ({ctx.author.id}) won with a {readable_user_card} against {bot.user}'s {readable_bot_card}")
    elif bot_card > user_card:  # or bot wins
        embeddesc = f"{bot.user.mention} won with a {readable_bot_card} against {ctx.author.mention}'s {readable_user_card}"
        embedcolor = discord.Color.red()
        logging.info(f"{bot.user} won with a {readable_bot_card} against {ctx.author}'s ({ctx.author.id}) {readable_user_card}")
    else:  # or it's a tie
        embeddesc = f"It's a tie! Both drew a {readable_user_card}"
        embedcolor = discord.Color.yellow()
        logging.info(f"{ctx.author} ({ctx.author.id}) tied with {bot.user} with {readable_user_card}")

    embed = discord.Embed(
        title="High Card Result",
        description=embeddesc,
        color=embedcolor
    )
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
    await ctx.reply(embed=embed, mention_author=True)
highcard.category = "fun"


@bot.hybrid_command(with_app_command=True, description="Play Rock Paper Scissors, default choice is scissors")
@app_commands.describe(choice="Your choice: rock, paper or scissors")
async def rps(ctx, choice: str = None):
    rps_choices = ["rock", "paper", "scissors"]
    embed = discord.Embed(
        title="$rps wrong usage",
        description="You're supposed to say either rock, paper or scissors",
        color=discord.Color.red()
        )
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")

    if choice is None:
        await ctx.reply(embed=embed, mention_author=True)
        logging.info(f"{ctx.author} ({ctx.author.id}) failed to provide either rock, paper or scissors (None)")
        return
    else:
        choice = choice.lower()
        if choice not in rps_choices:
            await ctx.reply(embed=embed, mention_author=True)
            logging.info(f"{ctx.author} ({ctx.author.id}) failed to provide either rock, paper or scissors ({choice})")
            return

    user_choice = choice.lower()  # make the input/argument lowercase
    bot_choice = secrets.choice(rps_choices)
    color = discord.Color.gold()

    if user_choice == bot_choice:
        result = "It's a tie!"
        color = discord.Color.gold()
        logging.info(f"{ctx.author} ({ctx.author.id}) tied to {bot.user} with {user_choice}")
    elif (user_choice == "rock" and bot_choice == "scissors") or \
         (user_choice == "scissors" and bot_choice == "paper") or \
         (user_choice == "paper" and bot_choice == "rock"):
        result = f"{ctx.author.mention} wins!"  # user wins
        color = discord.Color.green()
        logging.info(f"{ctx.author} ({ctx.author.id}) wins with {user_choice} against {bot.user}'s {bot_choice}")
    elif (bot_choice == "rock" and user_choice == "scissors") or \
         (bot_choice == "scissors" and user_choice == "paper") or \
         (bot_choice == "paper" and user_choice == "rock"):
        result = f"{bot.user.mention} wins!"  # bot wins
        color = discord.Color.red()
        logging.info(f"{bot.user} wins with {bot_choice} against {ctx.author}'s ({ctx.author.id}) {user_choice}")

    embed = discord.Embed(
        title="Rock Paper Scissors",
        description=(
            f"{ctx.author.mention} chose **{user_choice.capitalize()}**\n"  # New Lines for style
            f"{bot.user.mention} chose **{bot_choice.capitalize()}**\n\n"
            f"{result}"
        ),
        color=color
    )
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
    await ctx.reply(embed=embed, mention_author=True)
rps.category = "fun"


@bot.hybrid_command(with_app_command=True, description="The wisdom of the eight ball upon you", aliases=["8ball", "8b"])
@app_commands.describe(question="Your question is?")
async def eightball(ctx, question: str = None):
    yes_answers = [  # 7
        "yes", "why not", "absolutely", "hell yeah", "without a doubt", "absolutely", "uh, obviously"
    ]

    no_answers = [  # 7
        "no", "absolutely not", "fuck no", "nah", "are you stupid? no", "nuh uh", "not happening"
    ]

    unknown_answers = [  # 7
        "i'm not too sure", "i don't know", "the answer lies in the question itself",
        "the answer can be found in your soul", "do what your heart desires", "whatever you feel like",
        "idk, ask the next guy"
    ]

    eight_ball_answers = ["yes", "no", "unknown"]  # makes it equal chance for yes, no or unknown in case there are different amounts of strings in each list
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
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")

    await ctx.reply(embed=embed, mention_author=True)
    # For slash commands, ctx.message can be None; prefer the provided question if available
    q_text = question if question is not None else (getattr(getattr(ctx, "message", None), "content", "") or "")
    logging.info(f"{ctx.author}'s ({ctx.author.id}) 8ball answered to '{q_text}' with {eight_ball_real_choice}") 
eightball.category = "fun"


# --- GAMBLING COMMANDS ---


@bot.command(description="Literally just blackjack", aliases=["bj"])
async def blackjack(ctx):
    await ctx.reply("This command isn't complete yet! To be honest, I don't know if it ever will.", mention_author=True)
blackjack.category = "gambling"


@bot.command(description="Probably not exactly like poker, but close enough", aliases=["pk"])
async def poker(ctx):
    await ctx.reply("This command isn't complete yet! To be honest, I don't know if it ever will.", mention_author=True)
poker.category = "gambling"


@bot.command(description="Can you guess the bot's number?", aliases=["gnm"])
async def guessthenumber(ctx):
    await ctx.reply("This command isn't complete yet! To be honest, I don't know if it ever will.", mention_author=True)
guessthenumber.category = "gambling"


@bot.command(description="Trivia Time!!", aliases=["quiz"])
async def trivia(ctx):
    await ctx.reply("This command isn't complete yet! To be honest, I don't know if it ever will.", mention_author=True)
trivia.category = "gambling"


# --- INFO COMMANDS ---


@bot.hybrid_command(with_app_command=True, description="Shows this list!", aliases=["?"])
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
    logging.info(f"{ctx.author} ({ctx.author.id}) used the $help command")
help.category = "info"


@bot.hybrid_command(with_app_command=True, description="Show the bot's latency", aliases=["latency", "lag", "ms"])
async def ping(ctx):
    latency = round(bot.latency * 1000) # Copilot told me to multiply this by a thousand so
    embed = discord.Embed(
        title="Pong!",
        description=f"Latency: {latency} ms",
        color=discord.Color.gold()
    )
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
    await ctx.reply(embed=embed, mention_author=True)
    logging.info(f"{ctx.author} ({ctx.author.id}) used the $ping command ({latency}ms)")
ping.category = "info"


@bot.hybrid_command(with_app_command=True, description="Show how long the bot has been running", aliases=["lifetime", "upkeep"])
async def uptime(ctx):
    uptime_str = get_uptime()
    embed = discord.Embed(
        title="dotzbot's Uptime",
        description=f"The bot has been running for: {uptime_str}",
        color=discord.Color.gold()
    )
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
    await ctx.reply(embed=embed, mention_author=True)
    logging.info(f"{ctx.author} ({ctx.author.id}) used the $uptime command ({uptime_str})")
uptime.category = "info"


@bot.hybrid_command(with_app_command=True, description="General info about the bot", aliases=["bot", "about"])
async def botinfo(ctx):
    # Fetch commit code, by chatgpt ofc
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.github.com/repos/dotztv/dotzbot/commits") as resp:
            if resp.status == 200:
                data = await resp.json()
                latest_commit = data[0]
                commit_msg = latest_commit["commit"]["message"]
                commit_url = latest_commit["html_url"]
                commit_sha = latest_commit["sha"][:7]  # short sha
            else:
                commit_msg = "Could not fetch"
                commit_url = ""
                commit_sha = ""

    visible, hidden = get_command_count(bot)
    total = visible + hidden

    with open("discord.log", "r") as f:
        log_line_count = sum(1 for line in f)

    embed = discord.Embed(
        title="dotzbot",
        description="By <@550378971426979856> / Open-Source!",
        color=discord.Color.gold()
    )
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
    embed.add_field(name="Open-Source Info", value=f"", inline=False)
    embed.add_field(name="GitHub Link", value="[dotztv/dotzbot](https://github.com/dotztv/dotzbot)")
    embed.add_field(name="Latest Commit", value=f"[{commit_sha}]({commit_url})")
    embed.add_field(name="Commit Message", value=commit_msg)
    embed.add_field(name="Support", value="", inline=False)
    embed.add_field(name="Discord Server", value="[dotz's corner](https://discord.gg/WgzRu2NB7S)")
    embed.add_field(name="Developer DMs", value="@<550378971426979856>")
    embed.add_field(name="Software", value="", inline=False)
    embed.add_field(name="discord.py version", value=discord.__version__)
    embed.add_field(name="Python Version", value=platform.python_version())
    embed.add_field(name="Hosting", value="", inline=False)
    embed.add_field(name="Machine", value="Raspberry Pi 5")
    embed.add_field(name="Model", value="4GB Model")
    embed.add_field(name="Statistics", value="", inline=False)
    embed.add_field(name="Current Log Length", value=log_line_count)
    embed.add_field(name="Server Count", value=len(bot.guilds))
    embed.add_field(name="Command Amount", value=f"{total} ({hidden})") # for example, 9 total commands, 2 of which are hidden.

    await ctx.reply(embed=embed, mention_author=True)
    logging.info(f"{ctx.author} ({ctx.author.id}) used the $botinfo command")
botinfo.category = "info"


@bot.hybrid_command(with_app_command=True, description="Get info about a User", aliases=["user", "checkuser"])
async def userinfo(ctx, user_id: str = None): # Defaults arg to None, unless provided
    embed = discord.Embed( # Set the embed first to an error message
        title="$userinfo wrong usage",
        description="You're supposed to provide a user with a ping or their ID",
        color=discord.Color.red()
    )
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")

    if user_id is None: # Send the error if no argument is provided
        await ctx.reply(embed=embed, mention_author=True)
        logging.info(f"{ctx.author} ({ctx.author.id}) failed to use $userinfo ({ctx.message.content})")
        return
    elif user_id is not None: # Check if user_id was provided
        # Check if user_id is a ping
        if user_id.startswith("<@") and user_id.endswith(">"): 
            user_id = user_id.replace("<@", "").replace("!", "").replace(">", "") # Removes ping casing to get ID only
        # If it's not a ping, it's probably an ID
        else: 
            try: # if it isn't an ID, it'll raise ValueError and send the error message
                placeholder_variable = int(user_id) # placeholder_variable, cause if it's an actual variable; it'll crash for some reason
            except ValueError: # If it's not a UserID but instead some failed ping or something, it won't work
                await ctx.reply(embed=embed, mention_author=True)
                logging.info(f"{ctx.author} ({ctx.author.id}) failed to use $userinfo ({ctx.message.content})")
                return

    # Putting my full trust in the function above
    user_id = int(user_id) # Converts to int for fetch_user

    try: # Attempt to fetch the user, so we can use it for information
        user = await bot.fetch_user(user_id)
        member_obj = ctx.guild.get_member(user_id) if ctx.guild else None # gets member object if in a server -github copilot
        target_user = member_obj if member_obj else user # not going to lie, i dont know why this is here but i'm too scared to remove it
    except (discord.NotFound): # User doesn't exist
        await ctx.reply("User doesn't seem to exist? Try again with copying their ID or pinging them", mention_author=True)
        logging.error(f"{ctx.author} ({ctx.author.id}) provided a user we couldn't fetch? ({ctx.message.content})")
        return

    # Special people
    if user_id == 550378971426979856: # dotz
        description = "Hey, It's my creator!"
    elif user_id == 1267637358942224516: # dotzbot
        description = "Wait a minute, that's me!"
    else: # literally nobody
        description = ""

    embed = discord.Embed( # Changes the embed to the actual user info
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
    
    if member_obj and member_obj.roles:
        embed.add_field(
            name="Roles",
            value=", ".join([role.name for role in member_obj.roles if role.name != "@everyone"])
        )

    if target_user.avatar: # If they have a custom pfp
        embed.set_thumbnail(url=target_user.avatar.url) # Sets user's pfp as thumbnail (small, top right)
    
    if hasattr(user, "banner") and user.banner: # If they have a custom banner (Nitro Feature)
        embed.set_image(url=user.banner.url) # Sets user's banner as image (big, underneath)
    
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
    await ctx.reply(embed=embed, mention_author=True)
    logging.info(f"{ctx.author} ({ctx.author.id}) used {ctx.message.content}")
userinfo.category = "info"


@bot.hybrid_command(with_app_command=True, description="Get info about the current server", aliases=["server", "checkserver"])
async def serverinfo(ctx):
    if ctx.guild: # if run in a server (True)
        server_name = ctx.guild.name
        embed_desc = ""
        embed_color = discord.Color.green()
    else: # if not run a in a server, therefore DM (False)
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
    logging.info(f"{ctx.author} ({ctx.author.id}) used the $serverinfo command in {ctx.guild}")
serverinfo.category = "info"


# --- MODERATION COMMANDS ---
# consider permission check function


@bot.command(description="Bans the specified user", aliases=["begone"])
async def ban(ctx):
    await ctx.reply("This command isn't complete yet! To be honest, I don't know if it ever will.", mention_author=True)
ban.category = "moderation"


@bot.command(description="Kicks the specified user", aliases=["fuckoff"])
async def kick(ctx):
    await ctx.reply("This command isn't complete yet! To be honest, I don't know if it ever will.", mention_author=True)
kick.category = "moderation"


@bot.command(description="Times out the specified user", aliases=["shutup"])
async def timeout(ctx):
    await ctx.reply("This command isn't complete yet! To be honest, I don't know if it ever will.", mention_author=True)
timeout.category = "moderation"


@bot.command(description="Unbans the specified user", aliases=["sorry", "comeback"])
async def unban(ctx):
    await ctx.reply("This command isn't complete yet! To be honest, I don't know if it ever will.", mention_author=True)
unban.category = "moderation"


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
    logging.info(f"{ctx.author} ({ctx.author.id}) used $shutdown command!")
    logging.info(f"Bot was up for {get_uptime()}")
    await bot.close()
shutdown.category = "admin"


@bot.command(description="List all servers the bot is in (dotz only)", hidden=True, aliases=["servers"])
@commands.is_owner()
async def serverlist(ctx):
    embed = discord.Embed(
        title="Server List",
        description=f"The bot is in {len(bot.guilds)} servers:",
        color=discord.Color.gold()
    )

    for guild in bot.guilds: # Adds each guild as it's own field
        embed.add_field(
            name=guild.name,
            value=f"ID: {guild.id} | Members: {guild.member_count}",
            inline=False
        )
    await ctx.reply(embed=embed, mention_author=True)
    logging.info(f"{ctx.author} ({ctx.author.id}) used $serverlist command ({len(bot.guilds)} servers)")
serverlist.category = "admin"

@bot.command(description="Sync application commands globally (dotz only)", hidden=True)
@commands.is_owner()
async def synctree(ctx): # this entire command is written by copilot gpt5
    embed = discord.Embed(
        title="Syncing application commands",
        description="Attempting global sync...",
        color=discord.Color.gold()
    )
    embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
    await ctx.reply(embed=embed, mention_author=True)

    try:
        await bot.tree.sync()
        embed = discord.Embed(
            title="Global sync complete",
            description="Application commands have been synced globally.",
            color=discord.Color.green()
        )
        await ctx.reply(embed=embed, mention_author=True)
        logging.info(f"{ctx.author} ({ctx.author.id}) ran $synctree: global sync successful")
    except Exception as e:
        embed = discord.Embed(
            title="Global sync failed",
            description=f"Failed to sync application commands globally: {e}",
            color=discord.Color.red()
        )
        await ctx.reply(embed=embed, mention_author=True)
        logging.exception("Failed to globally sync application commands via $synctree")
synctree.category = "admin"

bot.run(TOKEN, log_handler=handler, log_level=logging.INFO)