import os
import re
import time
import json
import asyncpg

from discord.ext import commands
from dotenv import load_dotenv
from src.utils.custom_context import NewContext
from src.utils.errors import CurrentlyDevModeError
from src.cogs.meta import DoHelp

load_dotenv('src/.env')

with open('src/static-config.json', 'r') as config_file:
    config_file = json.load(config_file)


class BotBase(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        self.prefixes = {}
        self.config = config_file
        self.token = kwargs.pop('token')
        self.ignored_cogs = kwargs.pop('ignored_cogs')
        self.is_dev_mode = False
        self.connection_url = kwargs.pop('postgresql')
        self.db = None
        super().__init__(**kwargs)


    def update_config_file(self, content=None):
        if not content:
            content = self.config
        with open('src/static-config.json', 'w') as cf:
            json.dump(content, cf, indent=4)

    def load_cogs(self):
        """Loads all the necessary cogs."""
        for file in os.listdir("./src/cogs"):
            if file.endswith(".py") and file not in self.ignored_cogs:
                self.load_extension(f"cogs.{file[:-3]}")
        self.load_extension('jishaku')

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=NewContext)

    async def get_prefix(self, message):
        return self.prefixes.get(message.author.id, os.getenv('default_prefix'))

    def start_bot(self):
        """Starts the bot and logs into discord."""
        try:
            print('Connecting to database...')
            start = time.time()
            db = self.loop.run_until_complete(asyncpg.create_pool(self.connection_url))
            print(f'Connected to database. ({round(time.time() - start, 2)})s')
            self.db = db
        except Exception as e:
            print('Could not connect to database.')
            print(e)
        else:
            self.help_command = DoHelp()
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
    'command_prefix': '~',
    'postgresql': os.getenv('postgresql')}


client = BotBase(**bot_creds, owner_id=701494621162963044)


@client.event
async def on_ready():
    print(f'Bot connected on {time.strftime("%m/%d/%Y, %H:%M:%S")}')


@client.check
async def is_dev_mode(ctx):
    if client.is_dev_mode and ctx.author.id != client.owner_id:
        raise CurrentlyDevModeError
    else:
        return True


@client.event
async def on_message(message):
    json_config = client.config
    """Runs a few checks on every message that is sent."""
    if message.author.id == client.user.id:
        return
    if message.author.id in json_config['blacklisted-users'] or message.guild.id in json_config['blacklisted-guilds']:
        return
    if re.fullmatch("<@(!)?790632534350233630>", message.content):
        await message.channel.send(f'Hello! I am {client.user.name}. My prefix is "{client.command_prefix}". Use {client.command_prefix}help to get a list of commands.')
    if message.author.bot:
        return

    await client.process_commands(message)

if __name__ == '__main__':
    client.start_bot()
