import discord
import time
import os
import psutil
import datetime
import humanize
import platform
import sys

from discord.ext import commands


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process()

    @commands.command(name='ping',
                      brief='Check out the ping of the bot.',
                      help='Check the ping of the postgreSQL database and the websocket latency.')
    async def _ping(self, ctx):
        desc_embed = f'<:dataserver:790987826744393768> **Websocket**:`{round(self.bot.latency * 1000, 2)}`\n\n<:PostgreSQL:791377151991611412> **Database**:`{await self.bot.check_latency()}`'

        embed = discord.Embed(
            title='Latency:',
            description=desc_embed,
            color=discord.Color(0x2F3136)
        )
        start = time.time()
        message = await ctx.send(embed=embed)
        desc_embed += f'\n\n<a:typing:791381059468001280> **Typing**: `{round((time.time() - start) * 1000, 2)}`'
        embed = discord.Embed(
            title='Latency:',
            description=desc_embed,
            color=discord.Color(0x2F3136)
        )
        await message.edit(embed=embed)

    @commands.command(name='stats',
                      brief='Get some stats about me.',
                      help='Use ~stats to get info on me such as how many commands were run since the last restart or how much ram Im using, stuff like that.')
    async def _stats(self, ctx):
        await ctx.send(f'Commands since last reboot: {self.bot.commandsSinceLogon}\nI am currently in {len(self.bot.guilds)} guilds.')

    @commands.command(name='system', aliases=['sys'], help='Get useful information about the system, including ram, physical memory, process id, uptime & much more.', brief='Get system info.')
    async def _sys(self, ctx):
        embed = discord.Embed(
            title='System Information:',
            color=discord.Color(0x2F3136),
        )
        embed.add_field(name='**System:**', value=f'**Current OS:** `{platform.system()} {platform.architecture()[0]}`\n**Python Version:** `{platform.python_version()}`\n**Uptime:** `{humanize.naturaldelta(self.bot.uptime - datetime.datetime.utcnow())}`\n**Started at:** `{self.bot.uptime}`', inline=False)
        embed.add_field(name='\n**Memory:**', value=f'**Ram:** `{psutil.virtual_memory().percent}%`\n**PID:** `{os.getpid()}`\n**Physical memory:** `{humanize.naturalsize(self.process.memory_info().rss)}`')
        embed.add_field(name='Specs:', value=f'**Processor:** `{platform.processor()}`\n**Total ram:** `{humanize.naturalsize(psutil.virtual_memory().total)}`\n**CPU Count:** `{psutil.cpu_count()}`', inline=False)
        await ctx.temp_send(embed=embed)


def setup(bot):
    bot.add_cog(Utilities(bot))