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
                    help='Commands related to bookmarking messages.', invoke_without_command=True)
    async def _bookmark(self, ctx):
        await ctx.send(f'Did you mean: {self.bot.prefixes.get(ctx.author.id, "~")}bookmark add <id>?')

    @_bookmark.command(name='pinned', aliases=['pins'],
                       help='Bookmark all the pinned messages in the channel you execute the command in. Use flag --hidden to make all of em\' hidden')
    async def _pinned(self, ctx, args=""):
        parser = Arguments(add_help=False, allow_abbrev=False)
        parser.add_argument('--hidden', action='store_true')
        try:
            args = parser.parse_args(shlex.split(args))
        except Exception as e:
            await ctx.send(e)
        pins = await ctx.channel.pins()
        confirm = True
        if len(pins) > 3:
            confirm = await ctx.prompt(f'Holdup, you are about to bookmark {len(pins)} messages, do you wanna do this?')
        if len(pins) == 0:
            await ctx.send('There are no bookmarks to pin.')
            return
        if confirm:
            for message in pins:
                await ctx.bookmark(message, args, send_messages=False)
            await ctx.send(f'Successfully bookmarked {len(pins)} message(s).')
        else:
            await ctx.send('Aborting.')

    @commands.cooldown(1, 3, commands.BucketType.user)
    @_bookmark.command(name='add',
                       help='Add a bookmark by copying the ID or link of a message then using ~bookmark <id/link> you will only be able to get the jump url if you are viewing your bookmarks in the same server that you created them in. To avoid this use the flag --global when you create your bookmark.',
                       brief='Create a bookmark with some flags.',)
    async def _add(self, ctx, message: discord.Message, *, args: str = ''):
        parser = Arguments(add_help=False, allow_abbrev=False)
        parser.add_argument('--hidden', action='store_true')
        try:
            args = parser.parse_args(shlex.split(args))
        except Exception as e:
            await ctx.send(e)

        await ctx.bookmark(message, args)

    @commands.command(name='bookmarks',
                      brief='View your bookmarks.',
                      help='Use ~bookmarks to view all your bookmarks, you can add and remove folders.',
                      flags={'--show-hidden': 'Displays private flags (No arguments required.)',
                             '--show-id': 'Shows the id\'s of the bookmark.}'})
    async def _bookmarks(self, ctx, *, args: str = ''):
        await ctx.trigger_typing()
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

            message_info = await ctx.bookmark_from_cache(bookmark['database_id'])
            if not args.show_id:
                info = await self.bot.loop.run_in_executor(None, humanize.naturaltime, datetime.utcnow() - message_info['created_at'])
            else:
                info = bookmark['database_id']

            if not dm:
                if not bookmark['is_hidden']:
                    paginator.add_line(
                        f'[`{await trim_message(message_info["content"])}`]({message_info["jump_url"]}) • {info}')
            else:
                paginator.add_line(
                    f'[`{await trim_message(message_info["content"])}`]({message_info["jump_url"]}) • {info}')

                paginator.add_line(f'`Deleted message.`')
        # sends message, TODO add menu
        for page in paginator.pages:
            embed = discord.Embed(
                description=page,
                color=ctx.bot.embed_color
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
                        text='Use flag --show-id to see the bookmark ID\'s. Use flag --show-hidden to get a list of all your bookmarks hidden or not dm\'d to you.')
                    await message.edit(embed=embed)

    @_bookmark.command(name='remove', aliases=['del', 'delete', 'rem'],
                       brief='Remove a bookmark.',
                       help=f'Delete a bookmark using the ID. You can access the ID by reacting to the `ID` reaction when you view your bookmarks.')
    async def _remove_bookmark(self, ctx, bookmark_id: int):
        if await self.bot.db.fetch('SELECT FROM bookmarks WHERE database_id=$1 AND bookmark_owner_id=$2', bookmark_id,
                                   ctx.author.id):
            confirm = await ctx.prompt('Are you sure you would like to delete this bookmark?')

            if not confirm:
                await ctx.better_send('Aborting.')
            else:
                await ctx.delete_bookmark(bookmark_id)
                await ctx.temp_send('Successfully deleted bookmark.')
        else:
            await ctx.temp_send('Could not find bookmark, are you sure it exists, or you own it?')

    @_bookmark.command(name='clear',
                       brief='Clear all of your bookmarks',
                       help='Clear all of your bookmarks, be careful though, there is no undo.')
    async def _clear(self, ctx):
        confirm = await ctx.prompt('You are about to delete all of your bookmark! are you sure you would like to perform this action?')
        if not confirm:
            await ctx.send('Aborting.')
            return
        else:
            await self.bot.db.execute('DELETE FROM bookmarks WHERE bookmark_owner_id=$1', ctx.author.id)
            await ctx.send('Cleared bookmarks.')


def setup(bot):
    bot.add_cog(Bookmarking(bot))
