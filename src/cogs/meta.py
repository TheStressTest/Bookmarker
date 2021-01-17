import discord
from discord.ext import commands


class DoHelp(commands.HelpCommand):
    async def command_not_found(self, string):
        print(string)


class Meta(commands.Cog, name='Config'):
    def __init__(self, bot):
        self.bot = bot

    # sets your prefix.
    @commands.command(name='prefix', help='Set your custom prefix using ~prefix <prefix>')
    async def set_prefix(self, ctx,  prefix: str):
        query = 'INSERT INTO prefixes (prefix, owner_id) VALUES ($1, $2) ON CONFLICT (owner_id) DO UPDATE SET prefix = $3'
        await self.bot.db.execute(query, prefix, ctx.author.id, prefix)
        self.bot.prefixes[ctx.author.id] = str(prefix)
        await ctx.send(f'Successfully set your prefix to {prefix}')

    # caches prefixes into a dict, makes it easier for me obtain them
    @commands.Cog.listener()
    async def on_ready(self):
        prefix_dict = {}
        query = 'SELECT * FROM prefixes'
        prefixes = await self.bot.db.fetch(query)
        for prefix in prefixes:
            prefix_dict[prefix['owner_id']] = prefix['prefix']
        self.bot.prefixes = prefix_dict


def setup(bot):
    bot.add_cog(Meta(bot))