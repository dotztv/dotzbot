import discord
from discord.ext import commands
import secrets
import os

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Get a random (unmoderated) meme")
    async def meme(self, ctx):
        folder_path = "./memefolder"
        random_file = self.bot.get_random_file(folder_path)
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
        self.bot.printlog(ctx)
        if random_file:
            print(f'{ctx.author} got the meme {filenaming}')
        else:
            print('ERROR: No meme found in the memefolder!')

    @commands.command(description="Roll an X sided dice")
    async def roll(self, ctx, dicesides: int = 100):
        if dicesides <= 0:
            embed = discord.Embed(
                title="Dice Roll",
                description=f"{ctx.author.mention} just tried to roll a {dicesides}-sided dice",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
            await ctx.send(embed=embed)
        else:
            diceroll = 1 + secrets.randbelow(dicesides)
            embed = discord.Embed(
                title="Dice Roll",
                description=f"{ctx.author.mention} rolled a {dicesides}-sided dice and got {diceroll}",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
            await ctx.send(embed=embed)
            self.bot.printlog(ctx)
            if dicesides <= 0:
                print(f"{ctx.author} just tried to roll a {dicesides}-sided dice")
            else:
                print(f'{ctx.author}\'s {dicesides}-sided dice landed on {diceroll}')

    @commands.command(description="Flip a coin, Heads or tails?")
    async def coinflip(self, ctx):
        coinsides = ["heads", "tails"]
        coin = secrets.choice(coinsides)
        embed = discord.Embed(
            title="Coin Flip",
            description=f"{ctx.author.mention} flipped a coin and it landed on {coin}",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
        await ctx.send(embed=embed)
        self.bot.printlog(ctx)
        print(f'{ctx.author}\'s coin landed on {coin}')

    @commands.command(description="Highest card wins")
    async def highcard(self, ctx):
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
                description=f"{ctx.author.mention} won with a {readableusercard} against {self.bot.user.mention}'s {readablebotcard}",
                color=discord.Color.green()
            )
        elif winner == "bot":
            embed = discord.Embed(
                title="High Card Result",
                description=f"{self.bot.user.mention} won with a {readablebotcard} against {ctx.author.mention}'s {readableusercard}",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="High Card Result",
                description=f"It's a tie! Both drew a {readableusercard}",
                color=discord.Color.grey()
            )
        await ctx.send(embed=embed)
        self.bot.printlog(ctx)
        if winner == "user":
            print(f'{ctx.author} wins! {ctx.author}\'s {readableusercard} vs {self.bot.user}\'s {readablebotcard}')
        elif winner == "bot":
            print(f'{self.bot.user} wins! {self.bot.user}\'s {readablebotcard} vs {ctx.author}\'s {readableusercard}')
        else:
            print(f'ERROR: Error in {ctx.message.content}! Executed by {ctx.author} ({ctx.author.id}) at {self.bot.get_timenow()}')

    @commands.command(description="Play Rock Paper Scissors")
    async def rps(self, ctx, choice: str = "scissors"):
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
            result = f"{self.bot.user.mention} wins!"
            color = discord.Color.red()
        else:
            result = "Invalid choice! Please choose rock, paper, or scissors."
            color = discord.Color.red()

        embed = discord.Embed(
            title="Rock Paper Scissors",
            description=(
                f"{ctx.author.mention} chose **{userchoice.capitalize()}**\n"
                f"{self.bot.user.mention} chose **{botchoice.capitalize()}**\n\n"
                f"{result}"
            ),
            color=color
        )
        embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
        await ctx.send(embed=embed)
        self.bot.printlog(ctx)
        if result == f"{ctx.author.mention} wins!":
            print(f"{ctx.author} wins! {ctx.author}'s {userchoice} vs {self.bot.user}'s {botchoice}")
        elif result == f"{self.bot.user.mention} wins!":
            print(f"{self.bot.user} wins! {self.bot.user}'s {botchoice} vs {ctx.author}'s {userchoice}")
        elif result == "It's a tie!":
            print(f"{ctx.author} tied against {self.bot.user} in RPS")
        else:
            print(f'ERROR: Error in {ctx.message.content}! Executed by {ctx.author} ({ctx.author.id}) at {self.bot.get_timenow()}')

def setup(bot):
    bot.add_cog(Fun(bot))