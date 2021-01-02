import timeago
import discord
from datetime import datetime
from discord.ext import commands
from src.utils.custom_funcs import trim_message


class Bookmarking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='bookmark', invoke_without_command=True)
    async def _bookmark(self, ctx, message: discord.Message):
        await self.bot.db.execute(
            'INSERT INTO bookmarks (bookmark_owner_id, message_id, channel_id) VALUES ($1, $2, $3)',
            ctx.author.id, message.id, message.channel.id)

        await ctx.send('Bookmark added!')

    @commands.command(name='bookmarks',
                      brief='View your bookmarks.',
                      help='Use ~bookmarks to view all your bookmarks, you can add and remove folders.')
    async def _bookmarks(self, ctx):
        bookmarks = await self.bot.db.fetch('SELECT * from bookmarks WHERE bookmark_owner_id = $1',
                                            ctx.author.id)
        description_text = f'Total Bookmarks: {len(bookmarks)}\n'
        for bookmark in bookmarks:
            channel = self.bot.get_channel(bookmark['channel_id'])
            message_id = bookmark['message_id']

            message_info = await channel.fetch_message(message_id)
            description_text += f'\n[`{await trim_message(message_info.content)}`]({message_info.jump_url}) • {timeago.format(message_info.created_at, datetime.utcnow())}'

        embed = discord.Embed(
            description=description_text
        )
        embed.set_author(name='Your bookmarks:')
        await ctx.send(embed=embed)

    @_bookmark.command(name='remove',
                       brief='Remove a bookmark.',
                       help='Remove a bookmark by using ~bookmark remove <id>')
    async def _remove_bookmark(self, ctx, bookmark_id: int):

        confirm = await ctx.prompt('Are you sure you would like to delete this bookmark?')

        if not confirm:
            await ctx.better_send('Aborting.')
        else:
            await self.bot.db.execute('DELETE FROM bookmarks WHERE database_id=$1 AND bookmark_owner_id=$2',
                                      bookmark_id, ctx.author.id)
            await ctx.send('Successfully deleted bookmark.')


def setup(bot):
    bot.add_cog(Bookmarking(bot))
