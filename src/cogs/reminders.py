import discord
import asyncio
from discord.ext import commands
from src.utils.custom_funcs import time_convert as convert_time


class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='remind')
    async def _remind(self, ctx, time, *, reason='No reason.'):
        """"~remind <time> [reason]"""
        converted_time = await convert_time(time)
        if converted_time <= 86400:
            await asyncio.sleep(converted_time)
            await ctx.send(f'Done! You have been reminded for {reason} {ctx.author.mention}')
        else:
            await ctx.send('Invalid time format! Max time is 24 hours.')


def setup(bot):
    bot.add_cog(Reminder(bot))
