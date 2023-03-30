import discord
import logging
import os
import asyncio
import datetime
from discord.ext import commands
from discord.ext import commands, tasks
from discord.utils import get
from discord.ext.commands import Bot
import sys

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

TOKEN = "MTA4ODA0Nzc1NjQ4MTkyNTE1MQ.GH5v9B.5iP48faD3VKirPpg4WkS4y277K2bwoiGook0FY"


class YLBotClient(discord.Client):
    async def on_ready(self):
        logger.info(f'{self.user} has connected to Discord!')
        for guild in self.guilds:
            logger.info(
                f'{self.user} подключились к чату:\n'
                f'{guild.name}(id: {guild.id})')

    async def on_member_join(self, member):
        await member.create_dm()
        await member.dm_channel.send(
            f'Привет, {member.name}!'
        )

    async def on_message(self, message):
        if message.author == self.user:
            return
        symbol = open('prefix.txt', 'r').readline(1)
        if symbol == message.content.split()[0][0]:
            if f'{symbol}сменить префикс на' == ' '.join(message.content.split()[:-1]):
                with open('prefix.txt', 'w') as f:
                    f.write(message.content.split()[-1])
                await message.channel.send(f'префикс сменён на {message.content.split()[-1]}')
            else:
                await message.channel.send("Спасибо за сообщение")


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = YLBotClient(intents=intents)
client.run(TOKEN)

