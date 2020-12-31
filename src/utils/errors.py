from discord.ext.commands import CommandInvokeError


class InvalidTimeFormat(CommandInvokeError):
    """Gets raised when converting time in src/utils/custom_funcs fails"""
    pass


class NotATesterError(CommandInvokeError):
    """Gets raised when someone is not in self.bot.testers"""
    pass
