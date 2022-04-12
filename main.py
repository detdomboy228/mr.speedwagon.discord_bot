# from data import db_session
#
#
# def main():
#     db_session.global_init("db/blogs.db")
#
#
# if __name__ == '__main__':
#     main()
from data import db_session
from data.users import User
import discord
import pprint
from discord.ext import commands
from discord import FFmpegPCMAudio, voice_client
from discord.utils import get
from youtube_dl import YoutubeDL
from PIL import Image, ImageEnhance
import os
import json
import requests
import io
import random
import sqlite3
from simpledemotivators import Demotivator, Quote
import yandex_weather_api
import logging
import asyncio


# logger = logging.getLogger('discord')
# logger.setLevel(logging.DEBUG)
# handler = logging.StreamHandler()
# handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger.addHandler(handler)
bot = commands.Bot(command_prefix='!')
YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist': 'False', 'simulate': 'True',
               'preferredquality': '192', 'preferredcodec': 'mp3', 'key': 'FFmpegExtractAudio', 'quiet': True}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
queues = {}
queues_n = {}
sl_weather = {'clear': 'ясно',
              'partly-cloudy': 'малооблачно',
              'cloudy': 'облачно с прояснениями',
              'overcast': 'пасмурно',
              'drizzle': 'морось',
              'light-rain': 'небольшой дождь',
              'rain': 'дождь',
              'moderate-rain': 'умеренно сильный дождь',
              'heavy-rain': 'сильный дождь',
              'continuous-heavy-rain': 'длительный сильный дождь',
              'showers': 'ливень',
              'wet-snow': 'дождь со снегом',
              'light-snow': 'небольшой снег',
              'snow': 'снег',
              'snow-showers': 'снегопад',
              'hail': 'град',
              'thunderstorm': 'гроза',
              'thunderstorm-with-rain': 'дождь с грозой',
              'thunderstorm-with-hail': 'гроза с градом'}
now = {}
prev = {}
prev_n = {}


def check_queue(ctx, id):
    global queues_n, queues, prev, prev_n, now
    if queues[id] != {}:
        try:
            vc = ctx.guild.voice_client
            source = queues[id][0]
            if id not in now:
                prev_n[id] = 'rick astley - never gonna give you up --- 3 м. 32 с.'
                prev[id] = easy_convert('rick astley - never gonna give you up')[0]
            else:
                prev_n[id] = now[id]
                prev[id] = source
            vc.play(source, after=lambda x=0: check_queue(ctx, ctx.message.guild.id))
            now[id] = queues_n[id][0]
            del queues_n[id][0]
            del queues[id][0]
        except IndexError:
            queues[id] = []
            queues_n[id] = []


@bot.command(name='back', aliases=['b'])
async def back(ctx):
    global queues_n, queues, prev, prev_n
    id = ctx.message.guild.id
    a = easy_convert(prev_n[id])[0]
    b = prev_n[id]
    sss = easy_convert(prev_n[id])[-1]
    pprint.pp(sss)
    embed = discord.Embed(title='Отмотано к:', colour=0xff0000, url=sss['webpage_url'],
                          description=sss['title'])
    embed.set_author(name=sss['uploader'])
    embed.set_thumbnail(url=sss['thumbnails'][0]['url'])
    queues[id] = [a] + queues[id]
    queues_n[id] = [b] + queues_n[id]
    vc.stop()
    await ctx.reply(embed=embed, mention_author=False)


def easy_convert(name):
    info = ydl.extract_info(f"ytsearch:{name}", download=False)['entries'][0]
    arg = info['formats'][0]
    a = (FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=arg['url'], **FFMPEG_OPTIONS))
    return a, info


@bot.event
async def on_ready():
    global cur, db
    print('We have logged in as {0.user}'.format(bot))
    db = sqlite3.connect('ans.db')
    cur = db.cursor()
    if db:
        print('Database connected successfully')


@bot.command(aliases=['Hello'])
async def hello(ctx):
    author = ctx.message.author
    await ctx.reply(f'Привет, {author.mention}!', mention_author=False)


@bot.command(name='we')
async def we(ctx):
    global sl_weather
    try:
        if ctx.message.content.split('!we')[-1] and ctx.message.content.split('!we')[-1] != ' ':
            n = ctx.message.content.split('!we ')[-1].strip()
            x, y = requests.get(f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={n}&format=json").json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"].split()
            res = yandex_weather_api.get(requests, '5a57c893-985b-482d-a875-1f09c7151960', lat=y, lon=x)
            embed = discord.Embed(title='Погода',
                                  description=f'Температура: {str(res["fact"]["temp"])}°С\nОщущается как: {str(res["fact"]["feels_like"])}°С\nПогодные условия: {sl_weather[str(res["fact"]["condition"])]}\nВлажность: {str(res["fact"]["humidity"]) + "%"}\nСкорость ветра: {str(res["fact"]["wind_speed"]) + " М/С"}', colour=0x9999FF)
            embed.set_author(name='Яндекс.Погода', icon_url=f'https://yastatic.net/s3/home-static/_/37/37a02b5dc7a51abac55d8a5b6c865f0e.png')
            await ctx.send(embed=embed)
        else:
            await ctx.reply('Ну ты город-то введи', mention_author=False)
    except Exception:
        await ctx.reply('Команда !we не сработала(((', mention_author=False)


@bot.command(name='h')
async def help(ctx):
    embed = discord.Embed(title='Все команды бота:', colour=0xffff00)
    embed.add_field(name="!hello", value='Скажет "Привет";', inline=False)
    embed.add_field(name="!play или !p или !pl (желаемая песня)", value="""Включит в вашем голосовом канале
     желаемую музыку;""", inline=False)
    embed.add_field(name="!clear или !c", value="Очищает очередь из музыки;", inline=False)
    embed.add_field(name="!skip или !s", value="Пропускает музыку, которая идет сейчас;", inline=False)
    embed.add_field(name="!leave или !l", value="Покидает голосовой канал;", inline=False)
    embed.add_field(name="!cit (ваша цитата);(автор)", value="Оформляет цитату из введенных данных;", inline=False)
    embed.add_field(name="!mem (число)", value="Выдает шаблон для мема;", inline=False)
    embed.add_field(name="!mem_h", value="Выдает список самых популярных шаблонов для мемов;", inline=False)
    embed.add_field(name="!we (город или населенный пункт)", value="""Присылает текущее состояние погоды
     в вашем городе или населенном пункте;""", inline=False)
    embed.add_field(name="!rofl_h", value="Помощь по рофлам;", inline=False)
    embed.add_field(name="!rofl (число, обозначающее тип рофла)", value="""Присылает рофлянку введенной
     категории (!rofl_h);""", inline=False)
    embed.add_field(name="!dem (ваш текст) + прикрепите картинку", value="Подписывает картинку;", inline=False)
    embed.add_field(name="!shakal или !sh + прикрепите картинку", value="Шакалит картинку;", inline=False)
    await ctx.send(embed=embed)


@bot.command(aliases=['p', 'pl'])
async def play(ctx):
    global vc, url, ydl, queues_n, queues
    connected = ctx.author.voice
    ss = ctx.message.content.split()[0] + ' '
    url = ctx.message.content.split(ss)[-1]
    if not connected:
        await ctx.reply("Ну сам-то зайди тоже", mention_author=False)
        return
    if not ctx.voice_client:
        vc = await connected.channel.connect()
    else:
        vc = ctx.guild.voice_client
    ydl = YoutubeDL(YDL_OPTIONS)
    if 'https://' in url:
        info = ydl.extract_info(url, download=False)
    else:
        info = ydl.extract_info(f"ytsearch:{url}", download=False)['entries'][0]
    arg = info['formats'][0]['url']
    guild_id = ctx.message.guild.id
    if guild_id not in queues_n:
        queues_n[guild_id] = []
    if vc.is_playing():
        a = ydl.extract_info(f"ytsearch:{url}", download=False)
        b = a['entries'][0]
        if guild_id in queues:
            queues[guild_id].append((FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=arg, **FFMPEG_OPTIONS)))
        else:
            queues[guild_id] = [(FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=arg, **FFMPEG_OPTIONS))]
        embed = discord.Embed(title="Добавлено в очередь:", url=b['webpage_url'],
                              description=a['entries'][0]['title'],
                              colour=0xff0000)
        embed.set_author(name=a['entries'][0]['uploader'])
        embed.set_thumbnail(url=a['entries'][0]['thumbnails'][0]['url'])
        if int(b['duration']) > 60:
            m = int(b['duration']) // 60
            s = int(b['duration']) - int(b['duration']) // 60 * 60
            if m > 60:
                ch = m // 60
                ost_m = m - ch * 60
                embed.add_field(name="Длительность: ",
                                value=str(ch) + ' ч. ' + str(ost_m) + ' м. ' + str(s) + ' c.')
                queues_n[guild_id].append(b['title'] + ' --- ' + str(ch) + ' ч. ' + str(ost_m) + ' м. ' + str(s) + ' c.')
            else:
                embed.add_field(name="Длительность: ",
                                value=str(m) + ' м. ' + str(s) + ' c.')
                queues_n[guild_id].append(b['title'] + ' --- ' + str(m) + ' м. ' + str(s) + ' c.')

        else:
            embed.add_field(name="Длительность: ",
                            value=str(b['duration']) + ' c.')
            queues_n[guild_id].append(b['title'] + ' --- ' + str(b['duration']) + ' c.')
        await ctx.reply(embed=embed, mention_author=False)
    else:
        a = ydl.extract_info(f"ytsearch:{url}", download=False)
        b = a['entries'][0]
        embed = discord.Embed(title="Сейчас играет:", url=b['webpage_url'],
                              description=a['entries'][0]['title'],
                              colour=0xff0000)
        embed.set_author(name=a['entries'][0]['uploader'])
        embed.set_thumbnail(url=a['entries'][0]['thumbnails'][0]['url'])
        if int(b['duration']) > 60:
            m = int(b['duration']) // 60
            s = int(b['duration']) - int(b['duration']) // 60 * 60
            if m > 60:
                ch = m // 60
                ost_m = m - ch * 60
                embed.add_field(name="Длительность: ",
                                value=str(ch) + ' ч. ' + str(ost_m) + ' м. ' + str(s) + ' c.')
                queues_n[guild_id].append(b['title'] + ' --- ' + str(ch) + ' ч. ' + str(ost_m) + ' м. ' + str(s) + ' c.')
            else:
                embed.add_field(name="Длительность: ",
                                value=str(m) + ' м. ' + str(s) + ' c.')
                queues_n[guild_id].append(b['title'] + ' --- ' + str(m) + ' м. ' + str(s) + ' c.')

        else:
            embed.add_field(name="Длительность: ",
                            value=str(b['duration']) + ' c.')
            queues_n[guild_id].append(b['title'] + ' --- ' + str(b['duration']) + ' c.')
        if guild_id in queues:
            queues[guild_id].append((FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=arg, **FFMPEG_OPTIONS)))
        else:
            queues[guild_id] = [(FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=arg, **FFMPEG_OPTIONS))]
        check_queue(ctx, guild_id)
        await ctx.reply(embed=embed, mention_author=False)


@bot.command(aliases=['c'])
async def clear(ctx):
    global queues, queues_n
    queues = {}
    queues_n = {}
    embed = discord.Embed(title="Очередь была полностью очищена!",
                          colour=0xff0000)
    await ctx.reply(embed=embed, mention_author=False)


@bot.command(aliases=['s', 'ы'])
async def skip(ctx):
    try:
        global queues, now
        vc = ctx.guild.voice_client
        if vc.is_playing():
            if queues:
                embed = discord.Embed(title="Песня была успешно пропущена!",
                                      description=now[ctx.message.guild.id],
                                      colour=0xff0000)
                vc.stop()
                await ctx.reply(embed=embed, mention_author=False)
            else:
                vc.stop()
    except IndexError:
        pass


@bot.command(aliases=['q'])
async def queue(ctx):
    global queues_n, queues, now
    try:
        q = queues_n[ctx.message.guild.id]
        embed = discord.Embed(title='Текущая очередь из песен:', colour=0xff0000)
        embed.add_field(name='Играет прямо сейчас:', value=now[ctx.message.guild.id], inline=False)
        for i, e in enumerate(q):
            embed.add_field(name=str(i + 1) + ' - ', value=e, inline=False)
        await ctx.reply(embed=embed, mention_author=False)
    except Exception:
        embed = discord.Embed(title='Показывать нечего', colour=0xff0000)
        await ctx.reply(embed=embed, mention_author=False)


@bot.command(aliases=['l'])
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.reply('Ладно, я пошел. До связи!', mention_author=False)
    else:
        await ctx.reply('Да я и не подключен вроде', mention_author=False)


@bot.command(name='cit')
async def cit(ctx):
    try:
        img = Image.open(requests.get(ctx.message.attachments[0].url, stream=True).raw)
        img.save('example.png')
        if len(ctx.message.content.split('!cit ')[-1].split(';')) == 2:
            a = Quote(ctx.message.content.split('!cit ')[-1].split(';')[0],
                      ctx.message.content.split('!cit ')[-1].split(';')[-1])
        else:
            a = Quote(ctx.message.content.split('!cit ')[-1].split(';')[0], 'неизвестный мыслитель')
        a.create('example.png', result_filename='bebra.png')
        await ctx.reply(file=discord.File('bebra.png'), mention_author=False)
        os.remove('bebra.png')
        os.remove('example.png')
    except Exception:
        await ctx.reply('Ну ты что-то неправильно сделал', mention_author=False)


@bot.command(name='mem')
async def mem(ctx):
    try:
        if len(ctx.message.content.split()) == 2:
            n = int(ctx.message.content.split()[-1]) - 1
            res = (requests.get('https://api.imgflip.com/get_memes')).json()
            mem = res['data']['memes'][n]['url']
            await ctx.reply(mem, mention_author=False)
        else:
            n = int(ctx.message.content.split()[1]) - 1
            spn = ' '.join(ctx.message.content.split()[2:]).split(';')
            if len(spn) == int((requests.get('https://api.imgflip.com/get_memes')).json()['data']['memes'][n]['box_count']):
                dta = {'template_id':
                           (requests.get('https://api.imgflip.com/get_memes')).json()['data']['memes'][
                               n]['id'],
                       'username': 'mr.speedwagon', 'password': 'D1scordB0t', 'text0': spn[0], 'text1': spn[1]}
                print(dta)
                res = (requests.post('https://api.imgflip.com/caption_image',
                                     data=dta)).json()
                print(res)
                await ctx.reply(res['data']['url'], mention_author=False)
            else:
                await ctx.reply("Для создания мема неоходимо, чтобы кол-во полей в меме совпадало с кол-вом введенных подписей. Перепроверь данные", mention_author=False)
    except Exception:
        await ctx.reply('Видимо, ты забыл написать цифру после команды или же просто допустил ошибку(',
                        mention_author=False)


@bot.command(name='mem_h')
async def mem_h(ctx):
    try:
        n = int(ctx.message.content.split()[-1]) - 1
        res = (requests.get('https://api.imgflip.com/get_memes')).json()
        embed = discord.Embed(title='Текущий "топ" мемов:',
                              description=':white_check_mark: - подходит для создания мема\n :x: - не подходит',
                              colour=0xff0000)
        c = 1
        for i, e in enumerate(res['data']['memes']):
            if (i + 1 >= n * 10) and (i + 1 <= n * 10 + 10):
                if e['box_count'] > 2:
                    embed.add_field(name=str(c) + '. ',
                                    value=e['name'] + ' | ' + 'Кол-во полей: ' + str(e['box_count']) + ' | :x:',
                                    inline=False)
                else:
                    embed.add_field(name=str(c) + '. ',
                                    value=e['name'] + ' | ' + 'Кол-во полей: ' + str(e['box_count']) + ' | :white_check_mark:',
                                    inline=False)
            c += 1
        await ctx.reply(embed=embed, mention_author=False)
    except Exception:
        await ctx.reply('Возможно, ты забыл написать цифру-номер страницы', mention_author=False)


@bot.command(name='rofl_h')
async def rofl_h(ctx):
    try:
        embed = discord.Embed(title="Список команд для !rofl:", description="""
                1 - Анекдот;
                2 - Рассказы;
                3 - Стишки;
                4 - Афоризмы;
                5 - Цитаты;
                6 - Тосты;
                7 - Статусы;
                8 - Анекдот (+18);
                9 - Рассказы (+18);
                10 - Стишки (+18);
                11 - Афоризмы (+18);
                12 - Цитаты (+18);
                13 - Тосты (+18);
                14 - Статусы (+18);""", colour=0xff0000)
        await ctx.reply(embed=embed, mention_author=False)
    except Exception:
        await ctx.reply('Команда rofl_h не сработала(((', mention_author=False)


@bot.command(name='rofl')
async def rofl(ctx):
    try:
        n = ctx.message.content.split('!rofl ')[-1].strip()
        res = requests.get(f'http://rzhunemogu.ru/RandJSON.aspx?CType={n}').text
        res = res.replace('"content":"', "'content':'")
        res = res.replace('"}', "'}")
        t1 = ''
        for e in res:
            if e == '"':
                t1 += "'"
            elif e == "'":
                t1 += '"'
            else:
                t1 += e
        res = t1
        res = res.replace('\r', '     ')
        res = res.replace('\n', '    ')
        abc = json.loads(res)['content']
        itog = abc.replace('    ', '\n')
        itog = itog.replace('     ', '\r')
        await ctx.reply(itog, mention_author=False)
    except Exception:
        await ctx.reply('категории смешнявок можно изучить, вызвав команду !rofl_h', mention_author=False)


@bot.command(name='dem')
async def dem(ctx):
    try:
        img = Image.open(requests.get(ctx.message.attachments[0].url, stream=True).raw)
        img.save('example.png')
        if ';' in ctx.message.content:
            dem = Demotivator(ctx.message.content.split('!dem ')[-1].split(';')[0],
                              ctx.message.content.split('!dem ')[-1].split(';')[-1])
        else:
            dem = Demotivator(ctx.message.content.split('!dem ')[-1], '')
        dem.create('example.png', result_filename='bebra.png')
        await ctx.reply(file=discord.File('bebra.png'), mention_author=False)
        os.remove('example.png')
        os.remove('bebra.png')
    except Exception:
        await ctx.reply('ну ты что-то неправильно сделал', mention_author=False)


@bot.command(name='shakal', aliases=['sh'])
async def shakal(ctx):
    try:
        img = Image.open(requests.get(ctx.message.attachments[0].url, stream=True).raw)
        if img.size[0] > 2000 or img.size[-1] > 2000:
            img = img.resize((int(img.size[0] * 0.5), int(img.size[-1] * 0.5)))
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(600)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.85)
        img.save('example.png')
        await ctx.reply(file=discord.File('example.png'), mention_author=False)
        os.remove('example.png')
    except ValueError:
        await ctx.reply('тут не RGB, дурак. я это жрать не буду!!!!', mention_author=False)


@bot.event
async def on_message(message):
    global cur, db
    if message.author == bot.user:
        return
    elif ('пошел отсюда' in message.content.lower() or 'пошёл отсюда' in message.content.lower()) and \
            'бот' in message.content.lower():
        await message.channel.send('слушаюсь, мой господин')
    elif 'джозеф худший джоджо' in message.content.lower():
        await message.channel.send('полностью согласен!!!\nсамый крутой Джотаро')
    #################################
    elif 'кот' in message.content.lower() or 'кош' in message.content.lower():
        r = requests.get('https://api.thecatapi.com/v1/images/search').json()[0]['url']
        await message.channel.send(r)
    elif 'собак' in message.content.lower() or 'собач' in message.content.lower():
        r = requests.get('https://dog.ceo/api/breeds/image/random').json()['message']
        await message.channel.send(r)
    elif 'set timer in' in message.content.lower():
        try:
            h, m = int(message.content.lower().split('set timer in ')[-1].split('hours')[0]), \
                   int(message.content.lower().split('set timer in ')[-1].split()[2])
            s = h * 60 * 60 + m * 60
            await message.channel.send(f'The timer should start in {str(h)} hours and {str(m)} minutes.')
            await asyncio.sleep(s)
            await message.channel.send('Time X has come!')
        except Exception:
            pass
    #################################
    else:
        pass
    # вот тут СГЛЫПА
    db_sess = db_session.create_session()
    if len(db_sess.query(User).all()) < 500:
        if message.content:
            user = User()
            user.name = message.author.name + message.author.discriminator
            user.message = message.content
            db_sess.add(user)
            db_sess.commit()
    else:
        db_sess.query(User).filter(User.id == 1).delete()
        db_sess.commit()
        for userr in db_sess.query(User).all():
            userr.id -= 1
        user = User()
        user.name = message.author.name + message.author.discriminator
        user.message = message.content
        db_sess.add(user)
        db_sess.commit()
        await message.channel.send(random.choice(db_sess.query(User).filter(User.message.in_(message.content.split()) | User.message.like('%' + message.content + '%')).all()).message)
    # конец СГЛЫПЫ
    await bot.process_commands(message)


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    bot.run('bebra')


#User.message.like('%' + message.content + '%')
    # # вот тут СГЛЫПА
    # name = message.guild.name
    # cur.execute(f"""CREATE TABLE IF NOT EXISTS {name}(mess STR, id INT)""")
    # db.commit()
    # res = cur.execute(f"""SELECT * FROM {name}""").fetchall()
    # c = 0
    # for e in res:
    #     if str(message.content) == e[0]:
    #         c += 1
    # if c == 0 and ('!' not in message.content or message.content[0] != '!') and\
    #         '#' not in message.content and 'p!' not in message.content:
    #     cur.execute(f"""INSERT INTO {name}(mess, id) VALUES('{str(message.content)}', {int(len(res)) + 1})""")
    #     if len(res) + 1 > 500:
    #         cur.execute(f"""DELETE from {name} WHERE id = 1""")
    #         cur.execute(f"""UPDATE {name} SET id = id - 1""")
    #     db.commit()
    # sp = [e[0] for e in cur.execute(f"""SELECT * FROM {name}""").fetchall()]
    #
    # if len(sp) >= 500 and random.choice([0, 1, 2, 3]) == 3:
    #     if list(filter(lambda x: message.content.lower() in str(x).lower(), sp)):
    #         await message.channel.send(random.choice(list(filter(lambda x:
    #                                                              message.content.lower() in str(x).lower(), sp))))
    #     else:
    #         await message.channel.send(random.choice(sp))
    # # конец СГЛЫПЫ