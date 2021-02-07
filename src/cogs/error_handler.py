import discord
import traceback
import sys
import aiohttp

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

        elif isinstance(error, commands.BadArgument):
            await ctx.error('The argument you provided was invalid.', error)
            return

        elif isinstance(error, commands.ExpectedClosingQuoteError):
            await ctx.error('Did ya forget to add a closing quote?', error)
            return

        elif isinstance(error, commands.errors.MessageNotFound):
            await ctx.error('The message you used was invalid.', error)

        elif isinstance(error, commands.DisabledCommand):
            await ctx.error(f'{ctx.command} has been disabled.', error)

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.error('This command is on cooldown for you.', error)

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.error(error, error)

        else:
            self.bot.logger.error('\n' + ''.join(traceback.format_exception(type(error), error, error.__traceback__)))
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            tb = traceback.format_exception(type(error), error, error.__traceback__)

            print(''.join(tb), file=sys.stderr)

            # errors get sent to webhook
            if self.bot.webhook_url:
                async with aiohttp.ClientSession() as session:
                    embed = discord.Embed(
                        title='Ignoring exception in command {}:'.format(ctx.command),
                        description=f"""
                        ```py
                        {''.join(tb)}```
                        """,
                        color=discord.Color.red()
                    )
                    webhook = discord.Webhook.from_url(self.bot.webhook_url, adapter=discord.AsyncWebhookAdapter(session))
                    await webhook.send(username='Bookmarker errors.', embed=embed)

            await ctx.error('Aw snap, an uncaught error has occurred.', error, show_full_tb=True)

            return


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
