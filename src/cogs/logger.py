import discord
import os

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

    @commands.Cog.listener()
    async def on_command(self, ctx):
        self.bot.loop.run_in_executor(None, self.bot.logger.info, f'Command: "{ctx.message.content}" executed in {ctx.guild.name} ({ctx.guild.id}) by {ctx.author.id}')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.bot.loop.run_in_executor(None, self.bot.logger.info, f'Joined guild: {guild.name} ({guild.id})')

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        self.bot.loop.run_in_executor(None, self.bot.logger.info, f'Left guild: {guild.name} ({guild.id})')

    @commands.Cog.listener()
    async def on_shard_connect(self, shard):
        self.bot.loop.run_in_executor(None, self.bot.logger.info, f'Shard connected: {shard}')

    @commands.is_owner()
    @commands.command(name='del-logs')
    async def _del_logs(self, ctx):
        res = await ctx.prompt('Are you sure you would like to delete the logs?')
        if res:
            file = discord.File(fp='src/bot.log')
            await ctx.author.send('Backup just in case.', file=file)
            with open('src/bot.log', 'w') as logs:
                logs.write('')
            await ctx.send('Successfully cleared logs.')
        else:
            await ctx.better_send('Aborting.')


def setup(bot):
    bot.add_cog(Logging(bot))
