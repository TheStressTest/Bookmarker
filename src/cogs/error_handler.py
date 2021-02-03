import discord
import traceback
import sys

from src.utils import errors
from discord.ext import commands


class CommandErrorHandler(commands.Cog, command_attrs=dict(hidden=True)):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if hasattr(ctx.command, 'on_error'):
            return

        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound, )
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.errors.MessageNotFound):
            await ctx.send('The message you used was invalid.')
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')
            return

        if isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass
            return

        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send('This command is on cool-down for you.')
            return

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('One or more arguments are required for that command!')
            return

        if isinstance(error, errors.CurrentlyDevModeError):
            embed = discord.Embed(
                color=discord.Color(0xdda453),
                description='Developer mode is currently enabled. Sorry for the inconvenience!',
            )
            embed.set_author(name='⚠ | Developer mode enabled!')
            await ctx.temp_send(embed=embed)
            return

        else:
            self.bot.logger.error('\n' + ''.join(traceback.format_exception(type(error), error, error.__traceback__)))
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            return


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
