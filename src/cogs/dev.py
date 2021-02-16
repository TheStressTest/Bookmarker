import discord
from discord.ext import commands
from tabulate import tabulate
import subprocess
# from src.utils.fuzzy import extract


class DevTools(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if await self.bot.is_owner(ctx.author):
            return True
        else:
            raise commands.NotOwner()

    @commands.group(name='dev')
    async def _dev(self, ctx):
        pass

    @_dev.command(name='restart', aliases=['reboot'])
    async def _restart(self, ctx):
        await ctx.send('See ya in a bit. :wave:')
        await self.bot.change_presence(activity=discord.Game(name='Restarting...'))
        await ctx.bot.logout()
    
    @_dev.command(name='sync')
    async def _sync(self, ctx):
        confirm = await ctx.prompt('Are you sure you want to sync this bot? lol')
        if not confirm:
            await ctx.send('Ok. Aborting.')
            return
        out = subprocess.run(['git', 'pull'], capture_output=True, text=True)
        await ctx.send(f'```diff\n{out.stdout}```')
        await self.bot.logout()

    @_dev.command(name='call')
    async def _call(self, ctx, function):
        self.bot.dispatch(function)
        await ctx.send('done')

    @commands.group(name='devmode')
    async def _devmode(self, ctx):
        pass

    @_devmode.command(name='toggle')
    async def _toggle(self, ctx):
        if self.bot.is_dev_mode:
            self.bot.is_dev_mode = False
        else:
            self.bot.is_dev_mode = True

    @commands.command(name='sql')
    async def _sql(self, ctx, *, query):
        import time
        try:
            start = time.time()
            values = await self.bot.db.fetch(query)
            await ctx.temp_send(f'```\n{tabulate(values, list(values[0].keys()), tablefmt="psql")}\nSelected {len(values)} row(s) in {round(time.time() - start, 2)}s\n```')
        except Exception as e:
            await ctx.temp_send(f'```\n{e}\n```')

    @commands.group(name='blacklist')
    async def _blacklist(self, ctx):
        pass

    @_blacklist.command(name='guild')
    async def _guild(self, ctx, guild_id: int):
        guild = await self.bot.fetch_guild(guild_id)
        self.bot.config['blacklisted-guilds'].append(guild.id)
        await ctx.message.add_reaction('\U0001f44d')
        self.bot.update_config_file()

    @_blacklist.command(name='user')
    async def _user(self, ctx, user_id: int):
        user = await self.bot.fetch_user(user_id)
        self.bot.config['blacklisted-users'].append(user.id)
        await ctx.message.add_reaction('\U0001f44d')
        self.bot.update_config_file()


def setup(bot):
    bot.add_cog(DevTools(bot))