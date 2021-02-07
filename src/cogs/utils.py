import discord
import time
import os
import psutil
import datetime
import humanize
import platform

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
            color=ctx.bot.embed_color
        )
        start = time.time()
        message = await ctx.send(embed=embed)
        desc_embed += f'\n\n<a:typing:791381059468001280> **Typing**: `{round((time.time() - start) * 1000, 2)}`'
        embed = discord.Embed(
            title='Latency:',
            description=desc_embed,
            color=ctx.bot.embed_color
        )
        await message.edit(embed=embed)

    @commands.command(name='stats',
                      brief='Get some stats about me.',
                      help='Use ~stats to get info on me such as how many commands were run since the last restart or how much ram Im using, stuff like that.')
    async def _stats(self, ctx):
        await ctx.send(f'Commands since last reboot: {self.bot.commandsSinceLogon}\nI am currently in {len(self.bot.guilds)} guilds.')

    @commands.command(name='system', aliases=['sys'], help='Get useful information about the system, including ram, physical memory, process id, uptime & much more.', brief='Get system info.')
    async def _sys(self, ctx):
        self.process = psutil.Process(os.getpid())
        embed = discord.Embed(
            title='System Information:',
            color=ctx.bot.embed_color,
        )
        embed.add_field(name='**System:**', value=f'**Current OS:** `{platform.system()} {platform.architecture()[0]}`\n**Python Version:** `{platform.python_version()}`\n**Uptime:** `{humanize.naturaldelta(self.process.create_time() - time.time())}`\n**Started at:** `{datetime.datetime.fromtimestamp(self.process.create_time()).strftime("%a, %b %d, %Y %I:%M:%S")}`', inline=False)
        embed.add_field(name='\n**Memory:**', value=f'**Ram:** `{psutil.virtual_memory().percent}%`\n**PID:** `{os.getpid()}`\n**Physical memory:** `{humanize.naturalsize(self.process.memory_info().rss)}`')
        embed.add_field(name='Specs:', value=f'**Processor:** `{platform.processor()}`\n**Total ram:** `{humanize.naturalsize(psutil.virtual_memory().total)}`\n**CPU Count:** `{psutil.cpu_count()}`', inline=False)
        await ctx.temp_send(embed=embed)

    @commands.command(name='invite', brief='Invite me to your server.', help='Invite me to your server, optional argument: permission integer. If you want to invite me to your server with different permissions use this.')
    async def _invite(self, ctx, perm_int: int = 117824):
        await ctx.send(f'Thanks for inviting me!\n<https://discord.com/api/oauth2/authorize?client_id=790632534350233630&permissions={perm_int}&scope=bot>')

    @_invite.error
    async def _handle(self, ctx, error):
        await ctx.send('Invalid permission integer!')


def setup(bot):
    bot.add_cog(Utilities(bot))