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
