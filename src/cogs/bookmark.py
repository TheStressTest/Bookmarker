import humanize
import discord
import shlex
import argparse
import asyncio

from datetime import datetime
from discord.ext import commands
from src.utils.custom_funcs import trim_message


class Arguments(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)


class Bookmarking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='bookmark',
                    help='Commands, related to bookmarking messages.')
    async def _bookmark(self, ctx):
        pass

    @_bookmark.command(name='add',
                       help='Add a bookmark by copying the ID or link of a message then using ~bookmark <id/link> you will only be able to get the jump url if you are viewing your bookmarks in the same server that you created them in. To avoid this use the flag --global when you create your bookmark.',
                       brief='Create a bookmark with some flags.',
                       flags={
                           '--hidden': 'Makes your bookmark hidden to view hidden bookmarks run ~bookmarks --show-hidden'})
    async def _add(self, ctx, message: discord.Message, *, args: str = ''):
        parser = Arguments(add_help=False, allow_abbrev=False)
        parser.add_argument('--hidden', action='store_true')
        try:
            args = parser.parse_args(shlex.split(args))
        except Exception as e:
            await ctx.send(e)

        await self.bot.db.execute(
            'INSERT INTO bookmarks (bookmark_owner_id, message_id, channel_id, is_hidden) VALUES ($1, $2, $3, $4)',
            ctx.author.id, message.id, message.channel.id, args.hidden)

        await ctx.send('Bookmark added!')

    @commands.command(name='bookmarks',
                      brief='View your bookmarks.',
                      help='Use ~bookmarks to view all your bookmarks, you can add and remove folders.',
                      flags={'--show-hidden': 'Displays private flags (No arguments required.)',
                             '--show-id': 'Shows the id\'s of the bookmark.}'})
    async def _bookmarks(self, ctx, *, args: str = ''):
        dm = False

        # arg parse stuff
        parser = Arguments(add_help=False, allow_abbrev=False)
        parser.add_argument('--show-hidden', action='store_true', dest='hidden')
        parser.add_argument('--show-id', action='store_true', dest='show_id')
        try:
            args = parser.parse_args(shlex.split(args))
        except Exception as e:
            await ctx.send(e)

        if args.hidden:
            dm = True
        paginator = commands.Paginator(prefix='', suffix='')
        bookmarks = await self.bot.db.fetch('SELECT * from bookmarks WHERE bookmark_owner_id = $1',
                                            ctx.author.id)
        paginator.add_line(f'Total Bookmarks: {len(bookmarks)}\n')
        for bookmark in bookmarks:

            # configures message
            channel = self.bot.get_channel(bookmark['channel_id'])
            message_id = bookmark['message_id']
            message_info = await channel.fetch_message(message_id)

            if not args.show_id:
                info = humanize.naturaltime(datetime.utcnow() - message_info.created_at)
            else:
                info = bookmark['database_id']
            try:
                if not dm:
                    if not bookmark['is_hidden']:
                        paginator.add_line(
                            f'[`{await trim_message(message_info.content)}`]({message_info.jump_url}) • {info}')
                else:
                    paginator.add_line(
                        f'[`{await trim_message(message_info.content)}`]({message_info.jump_url}) • {info}')

            except (AttributeError, discord.NotFound):
                await self.bot.db.execute('DELETE FROM bookmarks WHERE message_id = $1', message_id)

                paginator.add_line(f'`Deleted message.`')

        # sends message, TODO add menu
        for page in paginator.pages:
            embed = discord.Embed(
                description=page,
                color=discord.Color(0x2F3136)
            )
            embed.set_author(name='Your bookmarks:')
            if not dm: embed.set_footer(text='React with \U00002139 to get some useful info.')
            author = ctx.author
            if dm:
                await ctx.message.add_reaction('\U0001f4ec')
                await author.send(embed=embed)
            else:

                message = await ctx.send(embed=embed)

                def check(payload):
                    if payload.message_id != message.id or payload.user_id != ctx.author.id:
                        return False
                    else:
                        return True

                await message.add_reaction('\U00002139')

                try:
                    await self.bot.wait_for('raw_reaction_add', check=check, timeout=120)

                except asyncio.TimeoutError:

                    embed.set_footer(text='Expired!')
                else:
                    embed.set_footer(
                        text='If you would like to view the id\' of the bookmark use the flag --show-id. Some messages may not have links and this is because they were bookmarked in another guild. If you would like to access all of your bookmarks with links run ~bookmarks --show-hidden. If you would like a bookmark to accessible anywhere use the flag --global when creating it.')
                    await message.edit(embed=embed)

    @_bookmark.command(name='remove', aliases=['del', 'delete'],
                       brief='Remove a bookmark.',
                       help=f'Delete a bookmark using the ID. You can access the ID by reacting to the `ID` reaction when you view your bookmarks.')
    async def _remove_bookmark(self, ctx, bookmark_id: int):
        if await self.bot.db.fetch('SELECT FROM bookmarks WHERE database_id=$1 AND bookmark_owner_id=$2', bookmark_id,
                                   ctx.author.id):
            confirm = await ctx.prompt('Are you sure you would like to delete this bookmark?')

            if not confirm:
                await ctx.better_send('Aborting.')
            else:
                await self.bot.db.execute('DELETE FROM bookmarks WHERE database_id=$1 AND bookmark_owner_id=$2',
                                          bookmark_id, ctx.author.id)
                await ctx.temp_send('Successfully deleted bookmark.')
        else:
            await ctx.temp_send('Could not find bookmark, are you sure it exists, or you own it?')


def setup(bot):
    bot.add_cog(Bookmarking(bot))
