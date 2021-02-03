import sys
import discord
import traceback

from discord.ext import commands
from src.utils.fuzzy import extract


class DoHelp(commands.HelpCommand):
    # TODO finish help command
    def get_command_signature(self, command):
        return f'{self.clean_prefix}{command.qualified_name} {command.signature}'

    async def send_command_help(self, command):
        embed = discord.Embed(
            title=self.get_command_signature(command)
        )
        embed.add_field(name='Help', value=command.help, inline=False)

        embed.add_field(name='TL;DR', value=command.brief, inline=False)

        if command.aliases:
            embed.add_field(name='Aliases', value=', '.join(command.aliases), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(
            title=group.name,
        )
        embed.add_field(name='Help', value=group.help, inline=False)

        embed.add_field(name='TL;DR', value=group.brief, inline=False)

        embed.add_field(name='Commands:', value=', '.join(str(group.walk_commands())), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def command_not_found(self, string):
        res = ''
        command_names = []
        for command in self.context.bot.walk_commands():
            command_names.append(command.name)
        _commands = extract(query=string, choices=command_names, limit=3, score_cutoff=70)

        for command in _commands:
            res += f'\n{command[0]}'

        return f'**Command {string} not found.**\nDid you mean...{res}...?'


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
        self.bot.logger.info('Started to cache prefix.')
        try:
            prefix_dict = {}
            query = 'SELECT * FROM prefixes'
            prefixes = await self.bot.db.fetch(query)
            for prefix in prefixes:
                prefix_dict[prefix['owner_id']] = prefix['prefix']
            self.bot.prefixes = prefix_dict
            self.bot.logger.info(f'Cached {len(prefixes)} prefixes.')
        except Exception as error:
            self.bot.logger.info(f'Failed to cache prefixes. {error}')
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(Meta(bot))