import discord
import logging
import sqlite3
from data.prefixs import Prefix
from data import db_session
import os
import asyncio
import datetime
from discord.ext import commands
from discord.ext import commands, tasks
from discord.utils import get
from discord.ext.commands import Bot
import sys
from data import db_session
from data.func import main

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
db_session.global_init("db/blogs.db")
db_sess = db_session.create_session()

TOKEN = "MTA4ODA0Nzc1NjQ4MTkyNTE1MQ.GXOh0e.qQkipDZuGkwFCsiZ5lzlG7v2vgFWoamZ4kCNb0"


class YLBotClient(discord.Client):
    async def on_ready(self):
        logger.info(f'{self.user} has connected to Discord!')
        for guild in self.guilds:
            logger.info(
                f'{self.user} подключились к чату:\n'
                f'{guild.name}(id: {guild.id})')
            ids = [i.server_id for i in db_sess.query(Prefix).all()]
            if guild.id in ids:
                continue
            else:
                server = Prefix()
                server.server_id = guild.id
                server.server_name = guild.name
                server.prefix = '!'
                server.russian_ruletka = 0
                db_sess.add(server)
                db_sess.commit()

    async def on_member_join(self, member):
        await member.create_dm()
        await member.dm_channel.send(
            f'Привет, {member.name}!'
        )

    async def on_message(self, message):
        if message.author == self.user:
            return
        mgi = message.guild.id
        mcs = message.content.split()
        symbol = db_sess.query(Prefix.prefix).filter(Prefix.server_id.like(mgi)).first()[0]
        if message.content == 'Префикс':
            await message.channel.send(f'Префикс ( {symbol} )')
        elif symbol == mcs[0][0]:
            if mcs[0] == f'{symbol}cprefix':
                if 3 > len(mcs) > 1 and mcs[-1] != '' and len(mcs[-1]) == 1:
                    prfx = db_sess.query(Prefix).filter(Prefix.server_id.like(mgi)).first()
                    prfx.prefix = mcs[-1]
                    db_sess.commit()
                    await message.channel.send(f'Префикс сменён на ( {mcs[-1]} )')
                else:
                    await message.channel.send('Не правильно указан префикс!')


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = YLBotClient(intents=intents)
client.run(TOKEN)
