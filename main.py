import discord
import logging
import sqlite3
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
            # con = sqlite3.connect('Servers_data.db')
            # cur = con.cursor()
            # ids = cur.execute("""SELECT server_id FROM servers_prefix""").fetchall()
            # if guild.id not in ids:
            #     cur.execute(f"""INSERT INTO servers_prefix(server_id, prefix)
            #                 VALUES({guild.id}, {'!'})""").fetchall()
            #     con.commit()
            #     con.close()

    async def on_member_join(self, member):
        await member.create_dm()
        await member.dm_channel.send(
            f'Привет, {member.name}!'
        )

    async def on_message(self, message):
        if message.author == self.user:
            return
        con = sqlite3.connect('Servers_data.db')
        cur = con.cursor()
        symbol = cur.execute(f"""SELECT prefix FROM servers_prefix
                             WHERE server_id LIKE {message.guild.id}""").fetchall()
        symbol = symbol[0][0]
        if symbol == message.content.split()[0][0]:
            if f'{symbol}сменить префикс на' == ' '.join(message.content.split()[:-1]):
                print(message.guild.id)
                cur.execute(f"""UPDATE servers_prefix
                            SET prefix = {message.content.split()[-1]}
                            WHERE server_id LIKE {message.guild.id}""").fetchall()
                con.commit()
                con.close()
                await message.channel.send(f'префикс сменён на {message.content.split()[-1]}')
            else:
                await message.channel.send("Спасибо за сообщение")


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = YLBotClient(intents=intents)
client.run(TOKEN)

