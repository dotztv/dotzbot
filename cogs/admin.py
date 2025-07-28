import discord
from discord.ext import commands
from datetime import datetime

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Shuts down the bot (dotz only)")
    @commands.is_owner()
    async def shutdown(self, ctx):
        timeatshutdown = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        embed = discord.Embed(
            title="dotzbot is offline",
            description=timeatshutdown,
            color=discord.Color.red()
        )
        embed.add_field(name="", value=f"Uptime: {self.bot.get_uptime()}")
        dotzbotchannel = self.bot.get_channel(1399359500049190912)
        await dotzbotchannel.send(embed=embed)
        print(f'Time is {timeatshutdown}')
        await self.bot.close()

    @commands.command(description="List all servers the bot is in (dotz only)")
    @commands.is_owner()
    async def serverlist(self, ctx):
        guilds = self.bot.guilds
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

def setup(bot):
    bot.add_cog(Admin(bot))