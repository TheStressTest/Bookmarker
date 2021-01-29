import discord
from discord.ext import commands


class Logging(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command(name='download-log')
    async def _download_log(self, ctx):
        await ctx.message.add_reaction('\U0001f4ec')
        file = discord.File(fp='src/bot.log')
        await ctx.author.send(file=file)


def setup(bot):
    bot.add_cog(Logging(bot))
