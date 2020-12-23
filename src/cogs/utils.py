import discord
from discord.ext import commands
import time


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ping command, usage: ~ping
    @commands.command()
    async def ping(self, ctx):
        desc_embed = f'<:dataserver:790987826744393768> **Websocket**:`{round(self.bot.latency * 1000, 2)}`\n\n<:PostgreSQL:791377151991611412> **Database**:`{await self.bot.check_latency()}`'

        embed = discord.Embed(
            title='Latency:',
            description=desc_embed,
            color=discord.Color(0x25262b)
        )
        start = time.time()
        message = await ctx.send(embed=embed)
        desc_embed += f'\n\n<a:typing:791381059468001280> **Typing**: `{round((time.time() - start) * 1000, 2)}`'
        embed = discord.Embed(
            title='Latency:',
            description=desc_embed,
            color=discord.Color(0x25262b)
        )
        await message.edit(embed=embed)


def setup(bot):
    bot.add_cog(Utilities(bot))