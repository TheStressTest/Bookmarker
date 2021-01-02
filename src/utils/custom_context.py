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