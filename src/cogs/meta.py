import discord
from discord.ext import commands


class Meta(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Meta(bot))