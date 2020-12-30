import discord
import asyncio
from discord.ext import commands
from src.utils.custom_funcs import time_convert as convert_time


class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='remind')
    async def _remind(self, ctx, time):
        converted_time = await convert_time(time)
        if int(converted_time) >= 86400:
            await asyncio.sleep(convert_time(time))
            await ctx.send('Done!')
        else:
            await ctx.send('Invalid time format! Max time is 24 hours.')


def setup(bot):
    bot.add_cog(Reminder(bot))