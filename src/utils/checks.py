from discord.ext import commands
from src.utils.errors import NotATesterError


def is_a_tester():
    """Checks if a user id is in self.bot.testers"""
    async def predicate(ctx):
        if ctx.author.id in ctx.bot.testers:
            return True
        else:
            raise NotATesterError
    return commands.check(predicate)

