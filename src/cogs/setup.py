import discord
from discord.ext import commands
# runs a few checks on ready


class Setup(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Leaves blacklisted guilds"""
        blacklisted_guilds = self.bot.config
        for guild in self.bot.guilds:
            if guild.id in blacklisted_guilds['blacklisted-guilds']:
                await guild.leave()
        await self.bot.change_presence(activity=discord.Game(name=f'{self.bot.command_prefix}help'), status=discord.Status.idle)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        blacklisted_guilds = self.bot.config
        if guild.id in blacklisted_guilds['blacklisted-guilds']:
            await guild.leave()


def setup(bot):
    bot.add_cog(Setup(bot))