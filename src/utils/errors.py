from discord.ext import commands


class InvalidTimeFormat(commands.CheckFailure):
    """Gets raised when converting time in src/utils/custom_funcs fails"""

    pass
