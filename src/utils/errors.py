from discord.ext import commands


class InvalidTimeFormat(commands.CommandInvokeError):
    """Gets raised when converting time in src/utils/custom_funcs fails"""
    pass


class NotATesterError(commands.CommandInvokeError):
    """Gets raised when someone is not in self.bot.testers"""
    pass


class InBotBlacklistError(commands.CommandError):
    """Gets raised when someone is in the bot blacklist"""
    pass
