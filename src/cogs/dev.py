import discord
from discord.ext import commands
from tabulate import tabulate


class DevTools(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if await self.bot.is_owner(ctx.author):
            return True
        else:
            raise commands.NotOwner()

    @commands.group(name='devmode')
    async def _devmode(self, ctx):
        pass

    @_devmode.command(name='toggle')
    async def _toggle(self, ctx):
        if self.bot.is_dev_mode:
            self.bot.is_dev_mode = False
        else:
            self.bot.is_dev_mode = True

    @commands.is_owner()
    @commands.command(name='sql')
    async def _sql(self, ctx, *, query):
        import time
        try:
            start = time.time()
            values = await self.bot.db.fetch(query)
            await ctx.temp_send(f'```\n{tabulate(values, list(values[0].keys()), tablefmt="psql")}\nSelected {len(values)} row(s) in {round(time.time() - start, 2)}s\n```')
        except Exception as e:
            await ctx.temp_send(f'```\n{e}\n```')


def setup(bot):
    bot.add_cog(DevTools(bot))