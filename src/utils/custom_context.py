from discord.ext import commands
import discord
import contextlib
import asyncio


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

    async def bookmark(self, message, args, cache=True):
        pool = self.bot.db
        query = 'INSERT INTO bookmarks (bookmark_owner_id, message_id, channel_id, is_hidden) VALUES ($1, $2, $3, $4)'
        await pool.execute(query, self.author.id, message.id, message.channel.id, args.hidden)

        if cache:
            _id = await pool.fetch('SELECT database_id FROM bookmarks WHERE message_id=$1 AND channel_id=$2 AND bookmark_owner_id=$3', message.id, message.channel.id, self.author.id)
            print(_id)
            # query = 'INSERT INTO semi_cached_bookmarks (content, jump_url, database_id) VALUES ($1, $2, $3)'
            # await pool.execute(query, message.content, message.jump_url, _id)
