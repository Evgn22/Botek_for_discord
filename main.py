import discord
import logging
import requests
from data.prefixs import Prefix
import asyncio
trigger = True
import random
from data import db_session

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
        global trigger
        if trigger and message.author == self.user:
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
                        players.players += f'{str(message.author.id)}:{message.author.name}:ALIVE:{roles.pop()}!@#?%'
                        db_sess.commit()
                        await message.channel.send(str(message.author.mention) + ' принят!')
                        if len(players.players.split('!@#?%')) > 8:
                            players.mafia = 2
                            await message.channel.send('Набор окончен!')
                            db_sess.commit()
                elif mafia == 2 and message.author == self.user and message.content == 'Набор окончен!':
                    trigger = True
                    players_info = [i.split(':') for i in players.players.split('!@#?%')]
                    for info in players_info[:-1]:
                        player = client.get_user(int(info[0]))
                        rules = ['Играть в мафию просто.',
                                 'Мафия убивает.', 'Врач лечит', 'Полицейский сожает за решётку',
                                 'ночная бабочка занимается своеобразными делами',
                                 'А мирные жители надеятся, что переживут ночь',
                                 'Игра длится пока мафия всех не убьёт или мирные жители не избавятся'
                                 ' от мафии путём голосования.']
                        txt = ':neutral_face:Ты мирный житель. Спи спокойно и надейся, что тебя не убьют.'
                        if info[3] == 'maf':
                            txt = ':skull:Ты мафия. Напиши мне ник того, кого хочешь убить. Не медли.'
                        elif info[3] == 'pol':
                            txt = ':cop:Ты Полицейский. Напиши мне ник того, кого хотел бы посадить.'
                        elif info[3] == 'pro':
                            txt = ':butterfly:Ты ночная бабочка. Напиши мне ник того, кого бы ты хотел охмурить.'
                        elif info[3] == 'doc':
                            txt = ':medical_symbol:Ты врач. Напиши ник того, кого вылечишь.'
                        await player.send('\n'.join(rules))
                        await player.send(txt)
                        if info == players_info[-2]:
                            players = db_sess.query(Prefix).filter(Prefix.server_id.like(mgi)).first()
                            players.mafia = 3
                            db_sess.commit()
                elif mafia == 3:
                    mai = message.author.id
                    players_ids = [int(i.split(':')[0]) for i in players.players.split('!@#?%')]
                    players_names = [i.split(':')[1] for i in players.players.split('!@#?%')]
                    if mai in players_ids and message.content in players_names:
                        info_author = [i.split(':') for i in players.players.split('!@#?%') if
                                       int(i.split(':')[0]) == mai]
                        players_info = [i.split(':') for i in players.players.split('!@#?%')]
                        players = db_sess.query(Prefix).filter(Prefix.server_id.like(mgi)).first()
                        for i in players_info:
                            if i[1] == message.content and info_author[2] != 'sovr':
                                if info_author[3] == 'maf':
                                    i[2] = 'died'
                                elif info_author[3] == 'pro':
                                    i[2] = 'sovr'
                                elif info_author[3] == 'doc':
                                    i[2] = 'ALIVE'
                                elif info_author[3] == 'pol':
                                    i[2] = 'turm'
                        players_info = [':'.join(i) for i in players_info]
                        players.players = '!@#?%'.join(players_info)
                        await message.channel.send('Принято.')
                        await asyncio.sleep(20)
                        players.mafia = 4
                        db_sess.commit()
                elif mafia == 4:
                    players = db_sess.query(Prefix).filter(Prefix.server_id.like(mgi)).first()
                    players_info = [i.split(':') for i in players.players.split('!@#?%')]
                    players_roles = [i.split(':')[3] for i in players.players.split('!@#?%')]
                    if 'maf' in list(set(players_roles)) and len(list(set(players_roles))) == 1:
                        pass

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
                    mafia.mafia = 0
                    trigger = False
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
