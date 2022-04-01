import discord
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


bot = commands.Bot(command_prefix='!')
YDL_OPTIONS = {'format': 'worstaudio/best', 'noplaylist': 'False', 'simulate': 'True',
               'preferredquality': '192', 'preferredcodec': 'mp3', 'key': 'FFmpegExtractAudio'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
queues = {}


def check_queue(ctx, id):
    try:
        if queues[id] != {}:
            try:
                vc = ctx.guild.voice_client
                source = queues[id].pop(0)
                vc.play(source, after=lambda x=0: check_queue(ctx, ctx.message.guild.id))
            except IndexError:
                pass
    except KeyError:
        pass


@bot.event
async def on_ready():
    global cur, db
    print('We have logged in as {0.user}'.format(bot))
    db = sqlite3.connect('ans.db')
    cur = db.cursor()
    if db:
        print('Database connected successfully')


@bot.command()
async def hello(ctx):
    author = ctx.message.author
    await ctx.send(f'Hello, {author.mention}!')


@bot.command(aliases=['p', 'pl'])
async def play(ctx):
    global vc
    connected = ctx.author.voice
    url = ctx.message.content.split('!p ')[-1]
    if not connected:
        await ctx.send("ну сам-то зайди тоже")
        return
    if not ctx.voice_client:
        vc = await connected.channel.connect()
    else:
        vc = ctx.guild.voice_client
    with YoutubeDL(YDL_OPTIONS) as ydl:
        if 'https://' in url:
            info = ydl.extract_info(url, download=False)
        else:
            info = ydl.extract_info(f"ytsearch:{url}", download=False)['entries'][0]
    arg = info['formats'][0]['url']
    if vc.is_playing():
        guild_id = ctx.message.guild.id
        if guild_id in queues:
            queues[guild_id].append((FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=arg, **FFMPEG_OPTIONS)))
        else:
            queues[guild_id] = [(FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=arg, **FFMPEG_OPTIONS))]
    else:
        vc.play((FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=arg, **FFMPEG_OPTIONS)),
                after=lambda x=0: check_queue(ctx, ctx.message.guild.id))


@bot.command(aliases=['c'])
async def clear(ctx):
    global queues
    queues = {}


@bot.command(aliases=['s'])
async def skip(ctx):
    try:
        global queues
        vc = ctx.guild.voice_client
        vc.stop()
    except IndexError:
        pass


@bot.command(aliases=['l'])
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send('да я и не подключен вроде')


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
        await ctx.send(file=discord.File('bebra.png'))
        os.remove('bebra.png')
        os.remove('example.png')
    except Exception:
        await ctx.reply('ну ты что-то неправильно сделал')


@bot.command(name='mem')
async def mem(ctx):
    try:
        n = int(ctx.message.content.split()[-1])
        res = (requests.get('https://api.imgflip.com/get_memes')).json()
        mem = res['data']['memes'][n]['url']
        await ctx.send(mem)
    except Exception:
        await ctx.reply('циферку чиркануть забыл или бред какой-то написал')


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
                8 - Статусы;
                11 - Анекдот (+18);
                12 - Рассказы (+18);
                13 - Стишки (+18);
                14 - Афоризмы (+18);
                15 - Цитаты (+18);
                16 - Тосты (+18);
                18 - Статусы (+18);""", colour=0xff0000)
        await ctx.send(embed=embed)
    except Exception:
        await ctx.reply('Команда rofl_h не сработала(((')


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
        await ctx.send(itog)
    except Exception:
        await ctx.reply('категории смешнявок можно изучить, вызвав команду !rofl_h')


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
        await ctx.send(file=discord.File('bebra.png'))
        os.remove('example.png')
        os.remove('bebra.png')
    except Exception:
        await ctx.reply('ну ты что-то неправильно сделал')


@bot.command(name='photo', aliases=['ph'])
async def photo(ctx):
    if 'шакал' in ctx.message.content:
        try:
            img = Image.open(requests.get(ctx.message.attachments[0].url, stream=True).raw)
            enhancer, e1 = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(600)
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(0.85)
            img.save('example.png')
            await ctx.send(file=discord.File('example.png'))
            os.remove('example.png')
        except ValueError:
            await ctx.reply('тут не RGB, дурак. я это жрать не буду!!!!')


@bot.event
async def on_message(message):
    global cur, db
    if message.author == bot.user:
        return
    elif ('пошел нахуй' in message.content.lower() or 'пошёл нахуй' in message.content.lower()) and \
            'бот' in message.content.lower():
        await message.channel.send('слушаюсь, мой господин')
    elif 'джозеф худший джоджо' in message.content.lower():
        await message.channel.send('полностью согласен!!!\nсамый крутой Джотаро')
    else:
        pass
    # вот тут СГЛЫПА
    name = message.guild.name
    cur.execute(f"""CREATE TABLE IF NOT EXISTS {name}(mess STR, id INT)""")
    db.commit()
    res = cur.execute(f"""SELECT * FROM {name}""").fetchall()
    c = 0
    for e in res:
        if str(message.content) == e[0]:
            c += 1
    if c == 0 and ('!' not in message.content or message.content[0] != '!') and\
            '#' not in message.content and 'p!' not in message.content:
        cur.execute(f"""INSERT INTO {name}(mess, id) VALUES('{str(message.content)}', {int(len(res)) + 1})""")
        if len(res) + 1 > 500:
            cur.execute(f"""DELETE from {name} WHERE id = 1""")
            cur.execute(f"""UPDATE {name} SET id = id - 1""")
        db.commit()
    sp = [e[0] for e in cur.execute(f"""SELECT * FROM {name}""").fetchall()]

    if len(sp) >= 500 and random.choice([0, 1, 2, 3]) == 3:
        if list(filter(lambda x: message.content.lower() in str(x).lower(), sp)):
            await message.channel.send(random.choice(list(filter(lambda x: message.content.lower() in str(x).lower(), sp))))
        else:
            await message.channel.send(random.choice(sp))
    # конец СГЛЫПЫ
    await bot.process_commands(message)


bot.run('bruh')


