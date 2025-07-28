import discord
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Shows this list!")
    async def help(self, ctx):
        embed = discord.Embed(
            title="dotzbot commands",
            description="",
            color=discord.Color.gold()
        )
        for command in self.bot.commands:
            embed.add_field(
                name=f"${command.name}",
                value=command.description or "No description.",
                inline=False
            )
            embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
        await ctx.send(embed=embed)
        self.bot.printlog(ctx)

    @commands.command(description="Show the bot's latency")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="Pong!",
            description=f"Latency: {latency} ms",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)
        self.bot.printlog(ctx)
        print(f'Reported Latency: {latency}')

    @commands.command(description="Show how long the bot has been running")
    async def uptime(self, ctx):
        uptime_str = self.bot.get_uptime()
        embed = discord.Embed(
            title="Uptime",
            description=f"The bot has been running for: {uptime_str}",
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Requested by {ctx.author} ({ctx.author.id})")
        await ctx.send(embed=embed)
        self.bot.printlog(ctx)
        print(f'Bot Uptime: {uptime_str}')

    @commands.command(description="General info about the bot")
    async def botinfo(self, ctx):
        await ctx.send("Command still in the works, so no info for you yet")
        self.bot.printlog(ctx)

    @commands.command(description="Get info about a UserID")
    async def userinfo(self, ctx, userid: int = 1267637358942224516):
        user = await self.bot.fetch_user(userid)
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
        self.bot.printlog(ctx)

    @commands.command(description="Get info about the current server")
    async def serverinfo(self, ctx):
        if ctx.guild is None:
            commandorigin = "DM"
        else:
            commandorigin = "Server"
        
        if commandorigin == "Server":
            servername = ctx.guild.name
        elif commandorigin == "DM":
            servername = "This is a DM"

        if servername == "This is a DM":
            embeddesc = "But I'll try to give you some information anyways"
        elif servername == ctx.guild.name:
            embeddesc = ""

        if commandorigin == "Server":
            embedcolor = discord.Color.green()
        elif commandorigin == "DM":
            embedcolor = discord.Color.gold()

        embed = discord.Embed(
            title=servername,
            description=embeddesc,
            color=embedcolor
        )
        if commandorigin == "Server":
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
        if commandorigin == "DM":
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
        self.bot.printlog(ctx)

def setup(bot):
    bot.add_cog(Info(bot))