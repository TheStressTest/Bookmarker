import timeago
import discord
from datetime import datetime
from discord.ext import commands
from src.utils.custom_funcs import trim_message


class Bookmark(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='bookmark', invoke_without_command=True)
    async def _bookmark(self, ctx, message: discord.Message):
        await self.bot.db.execute(
            'INSERT INTO bookmarks (bookmark_owner_id, message_id, channel_id) VALUES ($1, $2, $3)',
            ctx.author.id, message.id, message.channel.id)

        await ctx.send('Bookmark added!')

    @_bookmark.command(name='remove')
    async def test(self, ctx, bookmark_id):
        await ctx.send(bookmark_id)

    @commands.command(name='bookmarks')
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


def setup(bot):
    bot.add_cog(Bookmark(bot))
