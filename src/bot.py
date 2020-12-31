import discord
from discord.ext import commands
import os
import asyncpg
import time
from datetime import datetime


class BotBase(commands.Bot):
    def __init__(self, **kwargs):
        self.token = kwargs.pop('token')
        self.testers = kwargs.pop('testers')
        self.uptime = None
        self.db = None
        self.commandsSinceLogon = 0
        self.db_user = kwargs.pop('db_user')
        self.db_name = kwargs.pop('db_name')
        self.db_pass = kwargs.pop('db_pass')
        super().__init__(**kwargs)
    # self.db.execute() to execute sql commands, bot.db.execute outside of class

    def load_cogs(self):
        for file in os.listdir("./src/cogs"):
            if file.endswith(".py"):
                self.load_extension(f"cogs.{file[:-3]}")
        self.load_extension('jishaku')

    def start_bot(self):
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
            self.uptime = datetime.now()
            self.load_cogs()
            self.run(self.token)

# returns database latency in milliseconds.
    async def check_latency(self):
        start = time.time()
        await self.db.execute('SELECT 1;')
        return round((time.time() - start) * 1000, 2)


bot_creds = {
    "token": os.getenv('TOKEN'),
    'testers': [],
    'command_prefix': '~',
    'db_user': os.getenv('DB_USER'),
    'db_pass': os.getenv('DB_PASS'),
    'db_name': os.getenv('DB_NAME')}

client = BotBase(**bot_creds)


@client.event
async def on_ready():
    print(f'Bot connected on {time.strftime("%m/%d/%Y, %H:%M:%S")}')

if __name__ == '__main__':
    client.start_bot()
