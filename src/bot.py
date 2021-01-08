import os
import re
import asyncpg
import time

from discord.ext import commands
from datetime import datetime
from src.utils.custom_context import NewContext


class BotBase(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        self.user_blacklist = []
        self.token = kwargs.pop('token')
        self.testers = kwargs.pop('testers')
        self.ignored_cogs = kwargs.pop('ignored_cogs')
        self.uptime = None
        self.db = None
        self.cache = None
        self.commandsSinceLogon = 0
        self.db_user = kwargs.pop('db_user')
        self.db_name = kwargs.pop('db_name')
        self.db_pass = kwargs.pop('db_pass')
        super().__init__(**kwargs)

    def load_cogs(self):
        """Loads all the necessary cogs."""
        for file in os.listdir("./src/cogs"):
            if file.endswith(".py") and file not in self.ignored_cogs:
                self.load_extension(f"cogs.{file[:-3]}")
        self.load_extension('jishaku')

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=NewContext)

    async def on_command(self, ctx):
        if ctx.invoked_with != 'stats':
            self.commandsSinceLogon += 1

    def start_bot(self):
        """Starts the bot and logs into discord."""
        try:
            print('Connecting to database...')
            start = time.time()
            db = self.loop.run_until_complete(asyncpg.create_pool(database=self.db_name, user=self.db_user, password=self.db_pass))
            print(f'Connected to database. ({round(time.time() - start, 2)})s')
            self.db = db
        except Exception as e:
            print('Could not connect to database.')
            print(e)
        else:
            self.uptime = datetime.utcnow()
            self.load_cogs()
            self.run(self.token)

    async def check_latency(self):
        """Returns database latency in milliseconds"""
        start = time.time()
        await self.db.execute('SELECT 1;')
        return round((time.time() - start) * 1000, 2)



bot_creds = {
    "token": os.getenv('TOKEN'),
    'ignored_cogs': [],
    'testers': [],
    'command_prefix': '~',
    'db_user': os.getenv('DB_USER'),
    'db_pass': os.getenv('DB_PASS'),
    'db_name': os.getenv('DB_NAME')}

client = BotBase(**bot_creds, owner_id=701494621162963044)


@client.event
async def on_ready():
    print(f'Bot connected on {time.strftime("%m/%d/%Y, %H:%M:%S")}')


@client.event
async def on_message(message):
    """Runs a few checks on every message that is sent."""
    if message.author.id == client.user.id:
        return
    elif message.author.id in client.user_blacklist:
        return
    elif re.fullmatch("<@(!)?790632534350233630>", message.content):
        await message.channel.send(f'Hello! I am {client.user.name}. My prefix is "{client.command_prefix}". Use {client.command_prefix}help to get a list of commands.')
    elif message.author.bot:
        return

    await client.process_commands(message)

if __name__ == '__main__':
    client.start_bot()
