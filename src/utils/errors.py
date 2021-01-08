from discord.ext import commands


class InvalidTimeFormat(commands.CheckFailure):
    """Gets raised when converting time in src/utils/custom_funcs fails"""
    pass


class NotATesterError(commands.CheckFailure):
    """Gets raised when someone is not in self.bot.testers"""
    pass


class CurrentlyDevModeError(commands.CheckFailure):
    """Gets raised when developer mode is enabled."""
    pass
