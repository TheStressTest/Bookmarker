from discord.ext import commands
import discord
import contextlib
import asyncio
import traceback
import asyncpg  # to except errors


class NewContext(commands.Context):
    async def better_send(self, content=None, mention_author=False, **kwargs):
        """Replies if there is a message in between the command invoker and the bots message."""
        await asyncio.sleep(0.05)
        with contextlib.suppress(discord.HTTPException):
            if self.channel.last_message != self.message:
                return await self.reply(content, mention_author=mention_author, **kwargs)
        await self.send(content, **kwargs)

    async def clean_send(self, content=None, **kwargs):
        """Strips out @everyone and @here from the message."""
        zero_space = "​"
        await self.send(content.replace("@everyone", f"@{zero_space}everyone").replace("@here", f"@{zero_space}here"), **kwargs)

    async def error(self, title, error, show_full_tb=False, **kwargs):
        """Sends a message formatted as an error"""
        error_link = 'https://cdn.discordapp.com/attachments/796817574787547137/807450268269936690/error.png'
        author_id = kwargs.get('author_id', self.author.id)

        embed = discord.Embed(
            color=0xff0000
        )
        embed.set_author(name=f'{title}', icon_url=error_link)
        if show_full_tb:
            embed.set_footer(text='React to view the full traceback.')
        message = await self.send(embed=embed, **kwargs)
        if show_full_tb:

            def check(payload):
                if payload.message_id != message.id or payload.user_id != author_id:
                    return False
                else:
                    return True

            await message.add_reaction('<:error:807445634202075146>')

            try:
                await self.bot.wait_for('raw_reaction_add', check=check, timeout=120)
            except asyncio.TimeoutError:
                embed.set_footer(text='Error pane has expired')
            else:
                embed.description = f"""```py
                {''.join(traceback.format_exception(type(error), error, error.__traceback__))}```"""
                await message.edit(embed=embed)

    async def prompt(self, text: str, timeout=60.0, delete_after=True):
        """Adds a prompt, (yes or no)"""
        new_message = f'{text}\n\nReact with \N{WHITE HEAVY CHECK MARK} to confirm or \N{CROSS MARK} to deny.'

        author_id = self.author.id
        message = await self.send(new_message)

        def check(payload):
            nonlocal confirm
            if payload.message_id != message.id or payload.user_id != author_id:
                return False

            codepoint = str(payload.emoji)

            if codepoint == '\N{WHITE HEAVY CHECK MARK}':
                confirm = True
                return True
            elif codepoint == '\N{CROSS MARK}':
                confirm = False
                return True

            return False
        for emoji in ('\N{WHITE HEAVY CHECK MARK}', '\N{CROSS MARK}'):
            await message.add_reaction(emoji)

        try:
            await self.bot.wait_for('raw_reaction_add', check=check, timeout=timeout)
        except asyncio.TimeoutError:
            confirm = None
        try:
            if delete_after:
                await message.delete()
        finally:
            return confirm

    async def temp_send(self, content=None, **kwargs):
        """Reacts to the message with a wastebin emoji, if it is reacted to by the author, it will delete the message."""
        author_id = self.author.id
        message = await self.send(content, **kwargs)

        def check(payload):
            if payload.message_id != message.id or payload.user_id != author_id:
                return False
            else:
                return True

        await message.add_reaction('\U0001f5d1')
        try:
            await self.bot.wait_for('raw_reaction_add', check=check, timeout=120)
        except asyncio.TimeoutError:
            await message.delete()
        else:
            await message.delete()

    async def delete_bookmark(self, _id):
        pool = self.bot.db
        await pool.execute('DELETE FROM bookmarks WHERE database_id=$1', _id)
        await pool.execute('DELETE FROM semi_cached_bookmarks WHERE database_id=$1', _id)

    async def bookmark(self, message, args, cache=True, send_messages=True):
        pool = self.bot.db
        query = 'INSERT INTO bookmarks (bookmark_owner_id, message_id, channel_id, is_hidden) VALUES ($1, $2, $3, $4)'
        try:
            await pool.execute(query, self.author.id, message.id, message.channel.id, args.hidden)
            if send_messages:
                await self.send('Bookmark added!')
            if cache:
                _id = await pool.fetchrow(
                    'SELECT database_id FROM bookmarks WHERE message_id=$1 AND channel_id=$2 AND bookmark_owner_id=$3',
                    message.id, message.channel.id, self.author.id)
                query = 'INSERT INTO semi_cached_bookmarks (content, jump_url, created_at, database_id) VALUES ($1, $2, $3, $4)'
                await pool.execute(query, message.content, message.jump_url, message.created_at, _id['database_id'])

        except asyncpg.UniqueViolationError:
            if send_messages:
                await self.send('You can\'t bookmark the same message twice.')

    async def bookmark_from_cache(self, _id):
        pool = self.bot.db
        query = 'SELECT * FROM semi_cached_bookmarks WHERE database_id=$1'
        bookmark = await pool.fetchrow(query, _id)
        return bookmark
