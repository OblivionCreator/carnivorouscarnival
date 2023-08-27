import os

import disnake
from disnake.ext import commands
from disnake.ext.commands import Bot

bot = Bot(command_prefix='.', intents=disnake.Intents().all())

if __name__ == '__main__':
    for file in os.listdir('games'):
        if file.endswith('.py'):
            bot.load_extension(f'games.{file.split(".")[0]}')

bot.run(open('token.txt',encoding="utf8").read())