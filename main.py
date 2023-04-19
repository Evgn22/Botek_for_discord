import discord
import logging
import requests
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
import random
from data import db_session
from data.func import main

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
roles = ["doc", "maf", "ino", "pol", "pro", 'ino', 'maf', 'ino']
db_session.global_init("db/blogs.db")
db_sess = db_session.create_session()
thr = None

TOKEN = ""


class YLBotClient(discord.Client):
    async def on_ready(self):
        logger.info(f'{self.user} has connected to Discord!')
        for guild in self.guilds:
            logger.info(
                f'{self.user} подключились к чату:\n'
                f'{guild.name}(id: {guild.id})')
            ids = [i.server_id for i in db_sess.query(Prefix).all()]
            if guild.id == 1088054984190480395:
                global thr
                thr = guild.owner
            if guild.id in ids:
                continue
            else:
                server = Prefix()
                server.server_id = guild.id
                server.server_name = guild.name
                server.prefix = '!'
                server.mafia = 0
                server.chat = ''
                server.players = ''
                db_sess.add(server)
                db_sess.commit()

    async def on_message(self, message):
        if message.author == self.user:
            return
        if str(message.channel.type) != 'private':
            mgi = message.guild.id
            mcs = message.content.split()
            symbol = db_sess.query(Prefix.prefix).filter(Prefix.server_id.like(mgi)).first()[0]
            mafia = db_sess.query(Prefix.mafia).filter(Prefix.server_id.like(mgi)).first()[0]
            if message.content == 'prefix':
                await message.channel.send(f'Префикс ( {symbol} )')
            elif mafia:
                players = db_sess.query(Prefix).filter(Prefix.server_id.like(mgi)).first()
                chat = db_sess.query(Prefix.chat).filter(Prefix.server_id.like(mgi)).first()[0]
                if mafia == 1:
                    if message.content.lower() == 'я' and chat == str(message.channel):
                        players.players += f'{str(message.author)}:ALIVE:{roles.pop()}!@#?%'
                        db_sess.commit()
                        await message.channel.send(str(message.author.mention) + ' принят!')
                        if len(players.players.split('!@#?%')) > 8:
                            await message.channel.send('Набор окончен!')
                            players.mafia = 2
                            db_sess.commit()
            elif symbol == mcs[0][0]:
                if message.content == f'{symbol}help':
                    await message.author.send(
                        '\n'.join([f'Привет, {message.author.name}!',
                                   'На севере:',
                                   f'   1. Чтобы ещё раз получить инструкцию пропишите {symbol}help',
                                   '   2. Чтобы узнать текущий префикс напишите prefix',
                                   f'   3. Чтобы сменить префикс напишите {symbol}cprefix',
                                   f'   4. Чтобы сыграть в русскую рулетку пропишите {symbol}ruletka (число от 1 до 6)',
                                   f'   5. Чтобы сыграть в мафию пропишите {symbol}mafia',
                                   f'   6. Чтобы посмотреть на капибару пропишите {symbol}capybara',
                                   'В личном чате с ботом:',
                                   '    1. Чтобы посмотреть на капибару пропишите capybara',
                                   '    2. Чтобы сообщить об ошибке пропишите error (текст)',
                                   '    2.1. Также можно приложить картинки. ',
                                   '    2.2. Важно! Текст и картинки нужно отправлять одним сообщением.'])
                                                  )
                if mcs[0] == f'{symbol}cprefix':
                    if message.author == message.guild.owner:
                        if 3 > len(mcs) > 1 and mcs[-1] != '' and len(mcs[-1]) == 1:
                            prfx = db_sess.query(Prefix).filter(Prefix.server_id.like(mgi)).first()
                            prfx.prefix = mcs[-1]
                            db_sess.commit()
                            await message.channel.send(f'Префикс сменён на ( {mcs[-1]} )')
                        else:
                            await message.channel.send('Неправильно указан префикс!')
                    else:
                        await message.channel.send('Префикс может менять только создатель сервера')
                elif mcs[0] == f'{symbol}capybara':
                    response = requests.get('https://api.capy.lol/v1/capybara?json=true').json()
                    await message.channel.send(response['data']['url'])
                elif mcs[0] == f'{symbol}ruletka':
                    if 3 > len(mcs) > 1 and mcs[-1] in '123456' and len(mcs[-1]) == 1:
                        a = int(mcs[-1])
                        if a != random.randint(1, 6):
                            await message.channel.send('Чёртов везунчик.')
                        else:
                            await message.channel.send(':skull_crossbones: Тебе не повезло :skull_crossbones:')
                            role = message.guild.get_role(1094978465838669854)
                            await message.author.add_roles(role)
                            await message.author.move_to(None)
                            await asyncio.sleep(60)
                            await message.author.remove_roles(role)
                    else:
                        await message.channel.send('Сделай правильную ставку! Число от 1 до 6!')
                elif mcs[0] == f'{symbol}mafia' and not mafia:
                    await message.channel.send('@everyone Сбор мафии! Желающие сыграть напишите "я"')
                    mafia = db_sess.query(Prefix).filter(Prefix.server_id.like(mgi)).first()
                    mafia.mafia = 1
                    channel = db_sess.query(Prefix).filter(Prefix.server_id.like(mgi)).first()
                    channel.chat = str(message.channel)
                    db_sess.commit()
        else:
            if message.content == 'capybara':
                response = requests.get('https://api.capy.lol/v1/capybara?json=true').json()
                await message.channel.send(response['data']['url'])
            elif message.content.split()[0] == 'error':
                msg = await message.channel.fetch_message(message.id)
                await thr.send(embed=discord.Embed(description=f'!!!Error!!! {message.content[5:]}'))
                for i in range(len(message.attachments)):
                    await thr.send(f'{i + 1}.')
                    await thr.send(msg.attachments[i].url)
                await message.author.send('Спасибо за помощь, друг.')


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = YLBotClient(intents=intents)
client.run(TOKEN)
