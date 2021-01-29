import discord
import logging

from discord.ext import commands


class Logging(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s')
        logging
def setup(bot):
    bot.add_cog(Logging(bot))
