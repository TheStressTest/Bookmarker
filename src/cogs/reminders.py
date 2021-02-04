import asyncio
from discord.ext import commands
from src.utils.custom_funcs import time_convert as convert_time
import humanize


class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='remind',
                      help='Use ~remind <time> [reason] to remind yourself in X amount of minutes, example: ~remind 12m take out the cookies!',
                      brief='Give yourself a reminder.')
    async def _remind(self, ctx, time, *, reason='No reason.'):
        """"~remind <time> [reason]"""
        converted_time = await convert_time(time)
        if converted_time <= 86400:
            await ctx.message.add_reaction('👍')
            await ctx.send('Alright! Ill remind you then.')
            await asyncio.sleep(converted_time)
            await ctx.clean_send(f'Done! You have been reminded for {reason} {ctx.author.mention}')
        else:
            await ctx.send('Invalid time format! Max time is 24 hours.')


def setup(bot):
    bot.add_cog(Reminders(bot))
