import discord
from discord.ext import commands
# runs a few checks on ready


class Setup(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Leaves blacklisted guilds"""
        for guild in self.bot.guilds:
            if guild.id in await self.bot.get_json_config:
                await guild.leave()


def setup(bot):
    bot.add_cog(Setup(bot))