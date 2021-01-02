import discord
from discord.ext import commands
import time
import asyncio


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping',
                      brief='Check out the ping of the bot.',
                      help='Check the ping of the postgreSQL database and the websocket latency.')
    async def _ping(self, ctx):
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

    @commands.command(name='stats',
                      brief='Get some stats about me.',
                      help='Use ~stats to get info on me such as how many commands were run since the last restart or how much ram Im using, stuff like that.')
    async def _stats(self, ctx):
        await ctx.send(f'Commands since last reboot: {self.bot.commandsSinceLogon}\nI am currently in {len(self.bot.guilds)} guilds.')


def setup(bot):
    bot.add_cog(Utilities(bot))