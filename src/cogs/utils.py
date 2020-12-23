import discord
from discord.ext import commands
from src.bot import check_latency


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Cog {__name__} loaded')

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong! {await check_latency(self)}')


def setup(bot):
    bot.add_cog(Utilities(bot))