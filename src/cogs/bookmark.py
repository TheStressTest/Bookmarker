import discord
from discord.ext import commands


class Bookmark(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='bookmark', invoke_without_command=True)
    async def _bookmark(self, ctx, message: discord.Message):
        await self.bot.db.execute('INSERT INTO bookmarks (message_link, message_content, message_id, bookmark_owner_id) VALUES ($1, $2, $3, $4)',
                                  message.jump_url, message.content, message.id, ctx.author.id)

        await ctx.send('Bookmark added!')

    @_bookmark.command(name='remove')
    async def test(self, ctx, bookmark_id):
        await ctx.send(bookmark_id)


def setup(bot):
    bot.add_cog(Bookmark(bot))
