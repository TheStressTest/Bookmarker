import os
import re
import sys
import time
import json
import asyncpg
import logging
import traceback
import discord

from discord.ext import commands
from dotenv import load_dotenv
from utils.custom_context import NewContext
from cogs.meta import DoHelp
from logging.handlers import RotatingFileHandler

load_dotenv('src/.env')

with open('src/static-config.json', 'r') as config_file:
    config_file = json.load(config_file)


class BotBase(commands.AutoShardedBot):
    def __init__(self, **config):
        self.prefixes = {}
        self.logger = None
        self.config = config_file
        self.token = config.get('token')
        self.ignored_cogs = config.get('ignored_cogs')
        self.is_dev_mode = os.getenv('dev-mode') == 'true'
        self.connection_url = config.get('postgresql')
        self.db = None
        self.webhook_url = config.get('webhook_url', None)
        super().__init__(**config)

    def setup_logging(self, path):
        time_format = '%Y-%m-%d %H:%M:%S'
        max_bytes = 32 * 1024 * 1024  # 32 Mb
        self.logger = logging.getLogger(name='discord.bot')
        self.logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(filename=path, encoding='utf-8', mode='w', maxBytes=max_bytes, backupCount=3)
        _format = logging.Formatter('[%(asctime)s] [%(levelname)s] %(name)s: %(message)s', datefmt=time_format)
        handler.setFormatter(_format)
        self.logger.addHandler(handler)

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
                self.logger.info(f'loaded cog: {file}')
        self.load_extension('jishaku')

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=NewContext)

    async def get_prefix(self, message):
        return self.prefixes.get(message.author.id, self.command_prefix)

    def start_bot(self):
        """Starts the bot and logs into discord."""
        self.setup_logging('src/bot.log')
        try:
            print('Connecting to database...')
            start = time.time()
            db = self.loop.run_until_complete(asyncpg.create_pool(self.connection_url))
            print(f'Connected to database. ({round(time.time() - start, 2)})s')
            self.logger.info('Connected to database.')
            self.db = db
        except Exception as error:
            self.logger.error('Unable to connect to database: \n' + ''.join(traceback.format_exception(type(error), error, error.__traceback__)))
            self.logger.warning('Unable to connect to database. You will not have access to some commands.')
            print('Could not connect to database.', file=sys.stderr)
            print(error, file=sys.stderr)
        finally:
            self.help_command = DoHelp()
            self.load_cogs()
            self.run(self.token)

    async def check_latency(self):
        """Returns database latency in milliseconds"""
        start = time.time()
        await self.db.execute('SELECT 1;')
        return round((time.time() - start) * 1000, 2)


bot_creds = {
    'token': os.getenv('TOKEN'),
    'ignored_cogs': [],
    'command_prefix': os.getenv('default_prefix'),
    'postgresql': os.getenv('postgresql'),
    'webhook_url': os.getenv('webhook-url')}


client = BotBase(**bot_creds, owner_id=701494621162963044)


@client.event
async def on_ready():
    print(f'Bot connected on {time.strftime("%m/%d/%Y, %H:%M:%S")}')


@client.check
async def is_dev_mode(ctx):
    if client.is_dev_mode and ctx.author.id != client.owner_id:
        embed = discord.Embed(
            color=discord.Color(0xdda453),
            description='Developer mode is currently enabled. Sorry for the inconvenience!',
        )
        embed.set_author(name='⚠ | Developer mode enabled!')
        await ctx.temp_send(embed=embed)
    return True


@client.event
async def on_message(message):
    json_config = client.config
    """Runs a few checks on every message that is sent."""
    if message.author.id == client.user.id:
        return
    if message.author.id in json_config['blacklisted-users'] or message.guild.id in json_config['blacklisted-guilds']:
        return
    if re.fullmatch(r"<@(!)?790632534350233630>", message.content):
        await message.channel.send(f'Hello! I am {client.user.name}. Your prefix is "{client.prefixes.get(message.author.id, client.command_prefix)}". Use {client.prefixes.get(message.author.id, client.command_prefix)}help to get a list of commands.')
    if message.author.bot:
        return

    await client.process_commands(message)

if __name__ == '__main__':
    client.start_bot()