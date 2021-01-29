import discord
from discord.ext import commands
from tabulate import tabulate
# from src.utils.fuzzy import extract


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
    #
    # @commands.command(name='similar')
    # async def _similar(self, ctx, command_name):
    #     command_names = []
    #     for command in self.bot.walk_commands():
    #         command_names.append(command.name)
    #     await ctx.send('did you mean:')
    #     commands = extract(query=command_name, choices=command_names, limit=5)
    #     for command in commands:
    #         await ctx.send(command[0])

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