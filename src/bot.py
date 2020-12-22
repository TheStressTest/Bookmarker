import discord
from discord.ext import commands
from glob import glob
import os
import asyncpg
import time
from datetime import datetime


class BotBase(commands.Bot):
    def __init__(self, **kwargs):
        self.token = kwargs.pop('token')
        self.owner = kwargs.pop('owner')
        self.uptime = None
        self.commandsSinceLogon = 0
        # self.db_user = kwargs.pop('db_user')
        # self._db = kwargs.pop('db_name')
        # self.db_pass = kwargs.pop('db_pass')
        super().__init__(**kwargs)

    def start_bot(self):
        try:
            self.run(self.token)
            self.uptime = datetime.now()
        except KeyboardInterrupt:
            self.logout()


bot_creds ={
    "token": os.getenv('TOKEN'),
    'command_prefix': '~',
    'owner': 701494621162963044}

bot = BotBase(**bot_creds)


@bot.event
async def on_ready():
    print(f'Bot connected on {time.strftime("%m/%d/%Y, %H:%M:%S")}')

if __name__ == '__main__':
    bot.start_bot()
