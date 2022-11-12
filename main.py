# -*- coding: utf-8 -*-
from data import db_session
from data.users import User
import urllib.request
from urllib.parse import quote
import re
from static_ffmpeg import run
from bs4 import BeautifulSoup
import wikipedia as wi
import discord
import pprint
from discord.ext import commands
from discord import FFmpegPCMAudio, voice_client
from discord.utils import get
from youtube_dl import YoutubeDL
from  PIL import Image, ImageEnhance, ImageOps, ImageFilter
import os
import json
import requests
import io
import random
#from simpledemotivators import Demotivator, Quote 
import yandex_weather_api
import logging
import asyncio
from transliterate import translit
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger('discord')
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
client = discord.Client()
bot = commands.Bot(command_prefix='-')
YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist': 'False', 'simulate': 'True',
               'preferredquality': '192', 'preferredcodec': 'mp3', 'key': 'FFmpegExtractAudio',
               'logger': logger}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
queues = {}
queues_n = {}
sl_weather = {'clear': ['ясно', f'https://angarsk38.ru/wp-content/uploads/2018/06/15.jpg'],
              'partly-cloudy': ['малооблачно', f'https://region.center/source/VLADIMIR/2019/priroda/UUaXmnVzOl8.jpg'],
              'cloudy': ['облачно с прояснениями', f'http://dvinatoday.ru/upload/iblock/f93/072001_1394511601.jpg'],
              'overcast': ['пасмурно',
                           f'https://get.wallhere.com/photo/landscape-monochrome-architecture-building-sky-rain-photography-clouds-house-lightning-storm-England-evening-town-atmosphere-summer-British-thunder-Olympus-cloud-stormy-tree-cloudy-weather-houses-roof-cloudsstormssunsetssunrises-olympusomd-facade-black-and-white-monochrome-photography-residential-area-meteorological-phenomenon-cumulus-phenomenon-883443.jpg'],
              'drizzle': ['морось',
                          f'https://vsegda-pomnim.com/uploads/posts/2022-02/1645905858_2-vsegda-pomnim-com-p-moros-foto-7.jpg'],
              'light-rain': ['небольшой дождь', f'https://miro.medium.com/max/960/1*QbCmpwz1y-QHT4AzCZ9Fbg.jpeg'],
              'rain': ['дождь', f'https://proza.ru/pics/2020/08/03/94.jpg'],
              'moderate-rain': ['умеренно сильный дождь',
                                f'https://zanmsk.ru/wp-content/uploads/2019/08/ba956e0470cdd6a2ab6c7fafffdb9786978dc9c9.jpg'],
              'heavy-rain': ['сильный дождь',
                             f'https://avatars.mds.yandex.net/get-zen_doc/4375924/pub_60aca366d001161964edeae2_60aca3a3e3047f5161c1680a/scale_1200'],
              'continuous-heavy-rain': ['длительный сильный дождь',
                                        f'https://gazetaingush.ru/sites/default/files/news/20170623-v-ingushetii-ozhidayutsya-silnye-dozhdi-s-grozoy-i-gradom-mchs/dozhd_0.jpg'],
              'showers': ['ливень', f'https://dela.ru/medianew/img/1-9326785.jpg'],
              'wet-snow': ['дождь со снегом',
                           f'https://veved.ru/uploads/posts/2020-04/1587557186_d0b2619858db4e9bb83f12fb74d9f34f.max-1200x800.jpg'],
              'light-snow': ['небольшой снег',
                             f'https://img5.goodfon.ru/original/960x854/b/e6/kot-ryzhii-zima-sneg-snegopad.jpg'],
              'snow': ['снег', f'https://proprikol.ru/wp-content/uploads/2020/07/kartinki-idet-sneg-9.jpg'],
              'snow-showers': ['снегопад', f'https://ulpravda.ru/pictures/news/big/100703_big.jpg'],
              'hail': ['град', f'https://misanec.ru/wp-content/uploads/2018/07/grad.jpg'],
              'thunderstorm': ['гроза',
                               f'https://proprikol.ru/wp-content/uploads/2019/12/kartinki-pro-molniyu-i-grozu-26.jpg'],
              'thunderstorm-with-rain': ['дождь с грозой',
                                         f'https://static.mk.ru/upload/entities/2021/06/14/07/articles/facebookPicture/44/56/2a/d8/d41aa129d36ecf5f701a7f16e12a510e.jpg'],
              'thunderstorm-with-hail': ['гроза с градом',
                                         f'https://gorzavod.ru/wp-content/uploads/2019/07/llcUwlh_28k.jpg'],
              'cloudy-and-rain': ['облачно с дождем',
                                  f'https://avatars.mds.yandex.net/i?id=261b500f7f8885682b96e12db1a3c6b8_l-5315630-images-thumbs&n=13']}
WIKI_REQUEST = 'http://ru.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles='
now = {}
prev = {}
prev_n = {}
is_potok = {}
str_pr = {}
ffmpeg, ffprobe = run.get_or_fetch_platform_executables_else_raise()
c_z_matrix = {}
flag_c_z = {}
storona = {}
player = {}


def lyricsprs(url):
    res = requests.get(url)
    sp = BeautifulSoup(res.text, 'lxml')
    lrcs = sp.find('div', class_="Lyrics__Container-sc-1ynbvzw-6 YYrds")
    name = sp.find('title')
    a = lrcs.get_text('\n')
    print(a)
    return a, name.get_text()


def geturl(name):
    client_access_token = 'ctGDpRexTPVdfIwoeg47nUz_sFg2N9CmxRnoM_W-w4SecC2Mu0SPN3miHSSosRJ8'
    base_url = 'https://api.genius.com'
    user_input = name.replace(' ', '-')
    path = 'search/'
    request_url = '/'.join([base_url, path])
    print(request_url + user_input)
    params = {'q': user_input}
    token = 'Bearer {}'.format(client_access_token)
    headers = {'Authorization': token}
    r = requests.get(request_url, params=params, headers=headers)
    try:
        a = r.json()['response']['hits'][0]['result']['url']
    except Exception:
        a = None
    print(a)
    return a


def obrabotka_c_z(message):
    global c_z_matrix, flag_c_z, storona
    egor_loh = ['x', 'o']
    id = message.guild.id
    a = egor_loh[egor_loh.index(storona[id]) - 1]
    b = storona[id]
    if flag_c_z[id]:
        for elem in c_z_matrix[id]:
            if '' in elem:
                if elem.count(a) == 2:
                    for el in elem:
                        if not el:
                            elem[elem.index(el)] = a
                            return
        for elem in c_z_matrix[id]:
            if '' in elem:
                if elem.count(b) == 2:
                    for el in elem:
                        if not el:
                            elem[elem.index(el)] = a
                            return
        for i in range(3):
            if '' in [c_z_matrix[id][0][i], c_z_matrix[id][1][i], c_z_matrix[id][2][i]]:
                if [c_z_matrix[id][0][i], c_z_matrix[id][1][i], c_z_matrix[id][2][i]].count('x') == 2:
                    if c_z_matrix[id][0][i] == '':
                        c_z_matrix[id][0][i] = a
                    elif c_z_matrix[id][1][i] == '':
                        c_z_matrix[id][1][i] = a
                    elif c_z_matrix[id][2][i] == '':
                        c_z_matrix[id][2][i] = a
                    return
        for i in range(3):
            if '' in [c_z_matrix[id][0][i], c_z_matrix[id][1][i], c_z_matrix[id][2][i]]:
                if [c_z_matrix[id][0][i], c_z_matrix[id][1][i], c_z_matrix[id][2][i]].count(b) == 2:
                    if c_z_matrix[id][0][i] == '':
                        c_z_matrix[id][0][i] = a
                    elif c_z_matrix[id][1][i] == '':
                        c_z_matrix[id][1][i] = a
                    elif c_z_matrix[id][2][i] == '':
                        c_z_matrix[id][2][i] = a
                    return
        if '' in [c_z_matrix[id][0][0], c_z_matrix[id][1][1], c_z_matrix[id][2][2]]:
            if [c_z_matrix[id][0][0], c_z_matrix[id][1][1], c_z_matrix[id][2][2]].count(a) == 2:
                if c_z_matrix[id][0][0] == '':
                    c_z_matrix[id][0][0] = a
                elif c_z_matrix[id][1][1] == '':
                    c_z_matrix[id][1][1] = a
                elif c_z_matrix[id][2][2] == '':
                    c_z_matrix[id][2][2] = a
                return
        if '' in [c_z_matrix[id][0][0], c_z_matrix[id][1][1], c_z_matrix[id][2][2]]:
            if [c_z_matrix[id][0][0], c_z_matrix[id][1][1], c_z_matrix[id][2][2]].count(b) == 2:
                if c_z_matrix[id][0][0] == '':
                    c_z_matrix[id][0][0] = a
                elif c_z_matrix[id][1][1] == '':
                    c_z_matrix[id][1][1] = a
                elif c_z_matrix[id][2][2] == '':
                    c_z_matrix[id][2][2] = a
                return
        if '' in [c_z_matrix[id][0][2], c_z_matrix[id][1][1], c_z_matrix[id][2][0]]:
            if [c_z_matrix[id][0][2], c_z_matrix[id][1][1], c_z_matrix[id][2][0]].count(a) == 2:
                if c_z_matrix[id][0][2] == '':
                    c_z_matrix[id][0][2] = a
                elif c_z_matrix[id][1][1] == '':
                    c_z_matrix[id][1][1] = a
                elif c_z_matrix[id][2][0] == '':
                    c_z_matrix[id][2][0] = a
                return
        if '' in [c_z_matrix[id][0][2], c_z_matrix[id][1][1], c_z_matrix[id][2][0]]:
            if [c_z_matrix[id][0][2], c_z_matrix[id][1][1], c_z_matrix[id][2][0]].count(b) == 2:
                if c_z_matrix[id][0][2] == '':
                    c_z_matrix[id][0][2] = a
                elif c_z_matrix[id][1][1] == '':
                    c_z_matrix[id][1][1] = a
                elif c_z_matrix[id][2][0] == '':
                    c_z_matrix[id][2][0] = a
                return
        if storona[id] == 'o':
            if c_z_matrix[id] == [['', '', ''],
                                  ['', '', ''],
                                  ['', '', '']]:
                c_z_matrix[id][0][0] = 'x'
            elif (c_z_matrix[id][2][0] == 'x' or c_z_matrix[id][0][2] == 'x') and c_z_matrix[id][0][1] == 'o' and c_z_matrix[id][1][0] == 'o' and not c_z_matrix[id][2][2]:
                c_z_matrix[id][2][2] = 'x'
            elif c_z_matrix[id][2][0] == 'x' and c_z_matrix[id][1][0] == 'o' and c_z_matrix[id][2][1] == 'o' and not c_z_matrix[id][0][2]:
                c_z_matrix[id][0][2] = 'x'
            elif (c_z_matrix[id][0][1] == 'o' or c_z_matrix[id][2][1] == 'o' or c_z_matrix[id][2][2] == 'o') and not c_z_matrix[id][2][0]:
                c_z_matrix[id][2][0] = 'x'
            elif (c_z_matrix[id][1][0] == 'o' or c_z_matrix[id][1][2] == 'o' or c_z_matrix[id][2][2] == 'o') and not c_z_matrix[id][0][2]:
                c_z_matrix[id][0][2] = 'x'
            elif not c_z_matrix[id][2][2] and (c_z_matrix[id][0][2] == 'o' or c_z_matrix[id][2][0] == 'o' or c_z_matrix[id][1][1] == 'o'):
                c_z_matrix[id][2][2] = 'x'
        else:
            if c_z_matrix[id][0].count('x') + c_z_matrix[id][1].count('x') + c_z_matrix[id][2].count('x') == 1:
                if c_z_matrix[id][1][1] == 'x':
                    c_z_matrix[id][0][0] = 'o'
                else:
                    c_z_matrix[id][1][1] = 'o'
            elif c_z_matrix[id][0].count('x') + c_z_matrix[id][1].count('x') + c_z_matrix[id][2].count('x') == 2:
                if c_z_matrix[id][0][0] == 'x' or c_z_matrix[id][0][2] == 'x' or c_z_matrix[id][2][0] == 'x' or c_z_matrix[id][2][2] == 'x':
                    if (c_z_matrix[id][0][0] == 'x' and c_z_matrix[id][2][2] == 'x') or (c_z_matrix[id][0][2] == 'x' and c_z_matrix[id][2][0]):
                        c_z_matrix[id][0][1] = 'o'
                    elif c_z_matrix[id][1][1] == 'x' and c_z_matrix[id][2][2] == 'x' and not c_z_matrix[id][0][2]:
                        c_z_matrix[id][0][2] = 'o'
            elif c_z_matrix[id][0].count('x') + c_z_matrix[id][1].count('x') + c_z_matrix[id][2].count('x') == 3:
                if (c_z_matrix[id][0][0] == 'x' and c_z_matrix[id][2][0] == 'x' and c_z_matrix[id][1][2] == 'x') or \
                        (c_z_matrix[id][0][2] == 'x' and c_z_matrix[id][2][2] == 'x' and c_z_matrix[id][1][0] == 'x') or \
                        (c_z_matrix[id][0][0] == 'x' and c_z_matrix[id][0][2] == 'x' and c_z_matrix[id][2][1] == 'x') or \
                        (c_z_matrix[id][2][0] == 'x' and c_z_matrix[id][2][2] == 'x' and c_z_matrix[id][0][1] == 'x'):
                    if not c_z_matrix[id][0][1]:
                        c_z_matrix[id][0][1] = 'o'
                    elif not c_z_matrix[id][1][0]:
                        c_z_matrix[id][1][0] = 'o'
                    elif not c_z_matrix[id][1][2]:
                        c_z_matrix[id][1][2] = 'o'
                    else:
                        c_z_matrix[id][2][1] = 'o'
            if c_z_matrix[id][0].count('x') + c_z_matrix[id][1].count('x') + c_z_matrix[id][2].count('x') > \
                    c_z_matrix[id][0].count('o') + c_z_matrix[id][1].count('o') + c_z_matrix[id][2].count('o'):
                free_list = []
                for i in range(3):
                    for j in range(3):
                        if c_z_matrix[id][i][j] == '':
                            free_list.append((i, j))
                if free_list:
                    a = random.choice(free_list)
                    c_z_matrix[id][a[0]][a[1]] = 'o'
                else:
                    pass


def check_c_z(message):
    global c_z_matrix
    id = message.guild.id
    for elem in c_z_matrix[id]:
        if elem.count('o') == 3:
            return 'o'
        elif elem.count('x') == 3:
            return 'x'
    for i in range(len(c_z_matrix[id])):
        if c_z_matrix[id][0][i] == c_z_matrix[id][1][i] == c_z_matrix[id][2][i] == 'x':
            return 'x'
        elif c_z_matrix[id][0][i] == c_z_matrix[id][1][i] == c_z_matrix[id][2][i] == 'o':
            return 'o'
    if c_z_matrix[id][0][0] == c_z_matrix[id][1][1] == c_z_matrix[id][2][2] == 'x':
        return 'x'
    elif c_z_matrix[id][0][0] == c_z_matrix[id][1][1] == c_z_matrix[id][2][2] == 'o':
        return 'o'
    if c_z_matrix[id][0][2] == c_z_matrix[id][1][1] == c_z_matrix[id][2][0] == 'x':
        return 'x'
    elif c_z_matrix[id][0][2] == c_z_matrix[id][1][1] == c_z_matrix[id][2][0] == 'o':
        return 'o'
    if '' not in c_z_matrix[id][0] and '' not in c_z_matrix[id][1] and '' not in c_z_matrix[id][2]:
        return 'n'
    return None


def check_queue(ctx, id):
    global queues_n, queues, prev, prev_n, now
    if queues[id] != {}:
        vc = ctx.guild.voice_client
        try:
            if ctx.message.guild.id in is_potok:
                if is_potok[ctx.message.guild.id] is True:
                    return
            source = queues[id][0]
            if id not in now:
                prev_n[id] = 'rick astley - never gonna give you up --- 3 м. 32 с.'
                prev[id] = easy_convert('rick astley - never gonna give you up')[0]
            else:
                prev_n[id] = now[id]
                prev[id] = source
            now[id] = queues_n[id][0]
            asyncio.run_coroutine_threadsafe(send_message_to_channel(ctx, easy_convert(now[id])[-1]), client.loop)
            vc.play(source, after=lambda x=0: check_queue(ctx, ctx.message.guild.id))
            del queues_n[id][0]
            del queues[id][0]
        except IndexError:
            prev_n[id] = now[id]
            prev[id] = easy_convert(now[id])[0]
            queues_n[id] = []
            queues[id] = []


def check_potok(ctx, url, info, id):
    global queues_n, queues, prev, prev_n, now, str_pr
    if not discord.opus.is_loaded():
        discord.opus.load_opus('libopus.so')
    if not ctx.voice_client or not is_potok[id]:
        return
    if id not in str_pr:
        str_pr[id] = [info['title']]
    else:
        if len(str_pr[id]) >= 10:
            del str_pr[id][0]
        str_pr[id].append(info['title'])
    vc = ctx.guild.voice_client
    source = easy_convert(info['title'])[0]
    html = urllib.request.urlopen(url).read().decode()
    abc = html.split('Текущее видео')[-1]
    video_ids = re.findall(r"watch\?v=(\S{11})", abc)
    spis = []
    for e in video_ids:
        if e not in spis:
            spis.append(e)
    aboba = ''
    for e in spis:
        try:
            name = easy_convert("https://www.youtube.com/watch?v=" + e)[-1]['title']
        except Exception:
            continue
        if name not in str_pr[id]:
            counter = 0
            for e1 in info['title'].split():
                if e1 in name.split():
                    counter += 1
            if counter * 100 / len(name.split()) < 65:
                aboba = ("https://www.youtube.com/watch?v=" + e)
                break
    if not aboba:
        aboba = ("https://www.youtube.com/watch?v=" + spis[0])
    now[id] = info['title'] + ' --- '
    if int(info['duration']) > 60:
        m = int(info['duration']) // 60
        s = int(info['duration']) - int(info['duration']) // 60 * 60
        if m > 60:
            ch = m // 60
            ost_m = m - ch * 60
            now[id] += (str(ch) + ' ч. ' + str(ost_m) + ' м. ' + str(s) + ' c.')
        else:
            now[id] += (str(m) + ' м. ' + str(s) + ' c.')
    else:
        now[id] += (str(info['duration']) + ' c.')
    try:
        asyncio.run_coroutine_threadsafe(send_message_to_channel(ctx, easy_convert(info['title'])[-1]), client.loop)
        vc.play(source, after=lambda x=0: check_potok(ctx, aboba,
                                                      easy_convert(aboba)[-1],
                                                      id))
    except Exception as e:
        asyncio.run_coroutine_threadsafe(errsms(ctx, e), client.loop)
        return


def easy_convert(name):
    name = name.split(' --- ')[0]
    info = ydl.extract_info(f"ytsearch:{name}", download=False)['entries'][0]
    arg = info['formats'][0]
    a = (FFmpegPCMAudio(executable=ffmpeg, source=arg['url'], **FFMPEG_OPTIONS))
    os.system('youtube-dl --rm-cache-dir')
    return a, info


def get_wiki_image(search_term):
    try:
        result = wi.search(search_term, results=1)
        wi.set_lang('ru')
        wkpage = wi.WikipediaPage(title=result[0])
        title = wkpage.title
        response = requests.get(WIKI_REQUEST + title)
        json_data = json.loads(response.text)
        img_link = list(json_data['query']['pages'].values())[0]['original']['source']
        print(img_link)
        return img_link
    except:
        return 0


async def errsms(ctx, e):
    embed = discord.Embed(title="Ошибка воспроизведения:",
                          description=e,
                          colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                        random.randrange(0, 255),
                                                        random.randrange(0, 255)))
    mes = await ctx.reply(embed=embed, mention_author=False)
    await mes.add_reaction('❌')


async def send_message_to_channel(ctx, sss):
    embed = discord.Embed(title='Сейчас играет:', colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                                random.randrange(0, 255),
                                                                                random.randrange(0, 255)),
                          url=sss['webpage_url'],
                          description=sss['title'])
    embed.set_author(name=sss['uploader'])
    embed.set_thumbnail(url=sss['thumbnails'][-1]['url'])
    if int(sss['duration']) > 60:
        m = int(sss['duration']) // 60
        s = int(sss['duration']) - int(sss['duration']) // 60 * 60
        if m > 60:
            ch = m // 60
            ost_m = m - ch * 60
            embed.add_field(name="Длительность: ",
                            value='`' + str(ch) + ' ч. ' + str(ost_m) + ' м. ' + str(s) + ' c.`')
        else:
            embed.add_field(name="Длительность: ",
                            value='`' + str(m) + ' м. ' + str(s) + ' c.`')
    else:
        embed.add_field(name="Длительность: ",
                        value='`' + str(sss['duration']) + ' c.`')
    mes = await ctx.send(embed=embed)
    await mes.add_reaction('✅')


@bot.event
async def on_ready():
    global cur, db
    print('We have logged in as {0.user}'.format(bot))


@bot.event
async def on_message(message):
    global cur, db, flag_c_z, c_z_matrix
    id = message.guild.id
    if message.author == bot.user:
        return
    elif ('пошел отсюда' in message.content.lower() or 'пошёл отсюда' in message.content.lower()) and \
            'бот' in message.content.lower():
        await message.channel.send('слушаюсь, мой господин')
    elif ('бот го секс' in message.content.lower() or 'бот, го секс' in message.content.lower()) and \
             'бот' in message.content.lower():
        await message.channel.send(random.choice(['Го)))) Чур я сверху', 'Я не в настроении',
                                                  'Башка болит, потом как-нибудь',
                                                  'Я центральный персонаж 1 части джоджо. Го', 'Нет']))
    elif 'джозеф худший джоджо' in message.content.lower():
        await message.channel.send('полностью согласен!!!\nсамый крутой Джотаро')
    elif ('бот, скинь' in message.content.lower() or 'бот скинь' in message.content.lower()) and\
            len(set(message.content.lower().split()) & set(['хуй', 'член', 'пенис', 'бабиджон', 'биба', 'пэнис'])) >= 1:
        html = requests.get('https://yandex.ru/images/search?from=tabbar&text=хуй').text
        itog = re.findall(r'(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])',
                          html)
        sp = [e[0] + '://' + e[1] + e[2] for e in itog if
              '.jpg' in e[2] or '.png' in e[2] or '.bmp' in e[2] or '.gif' in e[2]]
        await message.channel.send(random.choice(["Это мой!!!", "Держи, сладкий", 'Блен, Максим, не стыдно???',
                                   'Держи кукан', 'Ну как, нравится?']))
        await message.channel.send(random.choice(sp[44:-17]))
    ################################
    elif 'кот' in message.content.lower() or 'кош' in message.content.lower():
        r = requests.get('https://api.thecatapi.com/v1/images/search').json()[0]['url']
        await message.channel.send(r)
    elif 'собак' in message.content.lower() or 'собач' in message.content.lower() or \
            'пес' in message.content.lower() or 'пёс' in message.content.lower():
        r = requests.get('https://dog.ceo/api/breeds/image/random').json()['message']
        await message.channel.send(r)
    ################################
    elif message.content in [str(x) for x in range(1, 10)] and flag_c_z[id]:
        if message.author.id == player[id]:
            if not c_z_matrix[id][(int(message.content) - 1) // 3][(int(message.content) - 1) % 3]:
                c_z_matrix[id][(int(message.content) - 1) // 3][(int(message.content) - 1) % 3] = storona[id]
                embed = discord.Embed(title='Крестики-нолики',
                                      description=f"{' '.join(list(map(lambda x: x.replace('', '- ') if not x else x, c_z_matrix[id][0])))}\n" + \
                                                  f"{' '.join(list(map(lambda x: x.replace('', '- ') if not x else x, c_z_matrix[id][1])))}\n" + \
                                                  f"{' '.join(list(map(lambda x: x.replace('', '- ') if not x else x, c_z_matrix[id][2])))}\n",
                                      colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                    random.randrange(0, 255),
                                                                    random.randrange(0, 255)))
                await message.channel.send(embed=embed, mention_author=False)
                if check_c_z(message) == storona[id]:
                    flag_c_z[id] = False
                    await message.channel.send('Я ПРОИГРАЛ, ТАКОГО БЫТЬ НЕ МОЖЕТ!!!!!!!!')
                elif check_c_z(message) and check_c_z(message) != 'n':
                    flag_c_z[id] = False
                    await message.channel.send('ХАХАХА, я победил, неуидивительно, с таким затупком играть')
                elif check_c_z(message) == 'n':
                    flag_c_z[id] = False
                    await message.channel.send('Ничья, ну такое бывает, достойно играешь!!!')
                if flag_c_z[id]:
                    obrabotka_c_z(message)
                    embed = discord.Embed(title='Крестики-нолики',
                                          description=f"{' '.join(list(map(lambda x: x.replace('', '- ') if not x else x, c_z_matrix[id][0])))}\n" + \
                                                      f"{' '.join(list(map(lambda x: x.replace('', '- ') if not x else x, c_z_matrix[id][1])))}\n" + \
                                                      f"{' '.join(list(map(lambda x: x.replace('', '- ') if not x else x, c_z_matrix[id][2])))}\n",
                                          colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                        random.randrange(0, 255),
                                                                        random.randrange(0, 255)))
                    await message.channel.send(embed=embed, mention_author=False)
                    if check_c_z(message) == storona[id]:
                        flag_c_z[id] = False
                        await message.channel.send('Я ПРОИГРАЛ, ТАКОГО БЫТЬ НЕ МОЖЕТ!!!!!!!!')
                    elif check_c_z(message) and check_c_z(message) != 'n':
                        flag_c_z[id] = False
                        await message.channel.send('ХАХАХА, я победил, неуидивительно, с таким затупком играть')
                    elif check_c_z(message) == 'n':
                        flag_c_z[id] = False
                        await message.channel.send('Ничья, ну такое бывает, достойно играешь!!!')
            else:
                await message.channel.send('Ты чего аферист? Эта клетка занята')
    else:
        pass
    if id not in flag_c_z:
        flag_c_z[id] = False
    if not flag_c_z[id]:
        c_z_matrix[id] = [['', '', ''],
                          ['', '', ''],
                          ['', '', '']]
        storona[id] = ''
    # вот тут СГЛЫПА
    db_sess = db_session.create_session()
    if message.content[0] != '-':
        if len(db_sess.query(User).filter(User.name_channel == message.guild.name).all()) < 500:
            if message.content:
                user = User()
                user.name_channel = message.guild.name
                user.name = message.author.name + message.author.discriminator
                user.message = message.content
                db_sess.add(user)
                db_sess.commit()
        else:
            id_u = db_sess.query(User).filter(User.name_channel == message.guild.name).all()[0].id
            db_sess.query(User).filter(User.id == id_u).delete()
            db_sess.commit()
            for userr in db_sess.query(User).all()[id_u - 1:]:
                userr.id -= 1
            db_sess.commit()
            user = User()
            user.name_channel = message.guild.name
            user.name = message.author.name + message.author.discriminator
            user.message = message.content
            mes_pul = db_sess.query(User).filter(
                User.message.in_(message.content.split()) | User.message.like('%' + message.content + '%')).all()
            if mes_pul:
                a = random.choice(mes_pul).message
                if a != message.content and random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 0]) == 0:
                    await message.channel.send(a)
            db_sess.add(user)
            db_sess.commit()
    # конец СГЛЫПЫ
    if random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]) == 3:
        sp = ['👎', '👍', '😭', '😎', '😋', '😠', '🤮'] + [bot.get_emoji(e.id) for e in message.guild.emojis]
        await message.add_reaction(random.choice(sp))
    await bot.process_commands(message)


class Speedwagon(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='hello')
    async def hello(self, ctx):
        author = ctx.message.author
        await ctx.reply(f'Привет, {author.mention}!', mention_author=False)

    @commands.command(name='cross_zero', aliases=['c_z', 'cz', 'ttt', 'tic-tac-toe'])
    async def cross_zero(self, ctx):
        global c_z_matrix, flag_c_z, storona, player
        id = ctx.message.guild.id
        if not flag_c_z[id]:
            flag_c_z[id] = True
            player[id] = ctx.message.author.id
            storona[id] = random.choice(['x', 'o'])
            await ctx.send(
                f'Игра запущена. Для игры пишите просто цифры от 1 до 9. Вы играете за: "{storona[id]}". Крестики ходят первые')
            if storona[id] == 'o':
                obrabotka_c_z(ctx)
            embed = discord.Embed(title='Крестики-нолики',
                                  description=f"{' '.join(list(map(lambda x: x.replace('', '-') if not x else x, c_z_matrix[id][0])))}\n" + \
                                              f"{' '.join(list(map(lambda x: x.replace('', '-') if not x else x, c_z_matrix[id][1])))}\n" + \
                                              f"{' '.join(list(map(lambda x: x.replace('', '-') if not x else x, c_z_matrix[id][2])))}\n",
                                  colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                random.randrange(0, 255),
                                                                random.randrange(0, 255)))
            await ctx.send(embed=embed, mention_author=False)
        else:
            await ctx.send('Игра уже запущена!!!!!!!!!')

    @commands.command(name='wiki')
    async def wiki(self, ctx):
        try:
            wi.set_lang('ru')
            embed = discord.Embed(title='Вот, что удалось найти:',
                                  description=wi.summary(ctx.message.content.split('-wiki ')),
                                  colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                random.randrange(0, 255),
                                                                random.randrange(0, 255)))
            embed.set_image(url=get_wiki_image(ctx.message.content.split('-wiki ')))
            embed.set_author(name="Wikipedia",
                             icon_url="https://festivalnauki.ru/upload/iblock/10c/10c4220955df61cfc0719fcddc1c52f4.jpg")
            await ctx.reply(embed=embed, mention_author=False)
        except Exception:
            await ctx.reply("Похоже, где-то была допущена ошибка, или такого вовсе не существует(")

    @commands.command(name='now')
    async def now(self, ctx):
        try:
            sss = easy_convert(now[ctx.message.guild.id])[-1]
            embed = discord.Embed(title='Играет прямо сейчас:', description=now[ctx.message.guild.id].split(' --- ')[0],
                                  colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                random.randrange(0, 255),
                                                                random.randrange(0, 255)),
                                  url=sss['webpage_url'])
            embed.set_author(name=sss['uploader'])
            embed.set_thumbnail(url=sss['thumbnails'][-1]['url'])
            embed.add_field(name='Длительность:', value='`' + now[ctx.message.guild.id].split(' --- ')[-1] + '`',
                            inline=False)
            await ctx.reply(embed=embed, mention_author=False)
        except Exception:
            await ctx.reply('Видимо, сейчас ничего не играет(', mention_author=False)
            return

    @commands.command()
    async def lyrics(self, ctx):
        try:
            ish_au = easy_convert(now[ctx.message.guild.id])[-1]['uploader']
            try:
                ish_au = translit(ish_au, reversed=True).replace("'", '')
            except Exception:
                pass
            ish_nm = now[ctx.message.guild.id].split(' --- ')[0]
            try:
                ish_nm = translit(ish_nm, reversed=True).replace("'", '')
            except Exception:
                pass
            auth = ish_au.split(' - Topic')[0].split('VEVO')[0]
            namev1 = ish_nm
            namev2 = namev1.split('(')[0].split('[')[0]
            namev3 = ''.join([e for e in namev1 if e != '(' and e != ')' and e != '[' and e != ']'])
            sp = {}
            try:
                a = lyricsprs(geturl(namev1))
                v1 = a[0]
                nm = a[-1]
                sp[nm] = v1
            except Exception:
                pass
            try:
                a = lyricsprs(geturl(auth + ' ' + namev1))
                v2 = a[0]
                nm = a[-1]
                sp[nm] = v2
            except Exception:
                pass
            try:
                a = lyricsprs(geturl(namev2))
                v3 = a[0]
                nm = a[-1]
                sp[nm] = v3
            except Exception:
                pass
            try:
                a = lyricsprs(geturl(auth + ' ' + namev2))
                v4 = a[0]
                nm = a[-1]
                sp[nm] = v4
            except Exception:
                pass
            try:
                a = lyricsprs(geturl(namev3))
                v5 = a[0]
                nm = a[-1]
                sp[nm] = v5
            except Exception:
                pass
            try:
                a = lyricsprs(geturl(auth + ' ' + namev3))
                v6 = a[0]
                nm = a[-1]
                sp[nm] = v6
            except Exception:
                pass
            sps = {}
            for e in sp:
                if e not in sps:
                    sps[e] = sp[e]
            if len(sps) > 0:
                await ctx.reply('**Вот всё, что я нашёл. Выбирай сам, короче**', mention_author=False)
            else:
                auth = ' '.join(((easy_convert(now[ctx.message.guild.id])[-1]['uploader']) + ' ').split())
                name_full = auth + ' ' + ' '.join(now[ctx.message.guild.id].split(' --- ')[0].split())
                html = urllib.request.urlopen(f'https://alloflyrics.cc/search/?s={quote(name_full)}').read()
                url = 'https://alloflyrics.cc/song/' + str(html).split('/song/')[1].split('">')[0]
                html = urllib.request.urlopen(url).read().decode('utf8')
                soup = BeautifulSoup(html, 'lxml')
                if soup.find_all('p')[0].get_text().split()[0] == 'Из':
                    r = soup.find_all('p')[0].get_text() + '\n' + soup.find_all('p')[1].get_text()
                else:
                    r = soup.find_all('p')[0].get_text()
                namus = soup.find('title')
                with open("song_text.txt", "w") as file:
                    file.write(r)
                await ctx.reply('**Вот всё, что я нашёл. Выбирай сам, короче**', mention_author=False)
                await ctx.send(namus.get_text())
                await ctx.send(file=discord.File("song_text.txt"), mention_author=False)
                os.remove('song_text.txt')
            for e in sps:
                with open("song_text.txt", "w", encoding="utf-8") as file:
                    file.write(sps[e])
                await ctx.send(e)
                await ctx.send(file=discord.File("song_text.txt"))
                os.remove('song_text.txt')
        except Exception:
            await ctx.reply('Видимо, произошла ошибка( Текста нема.', mention_author=False)

    @commands.command(name='pause')
    async def pause(self, ctx):
        try:
            try:
                vc = ctx.guild.voice_client
            except Exception:
                ctx.reply('Ну сам-то зайди тоже', mention_author=False)
            vc.pause()
            mes = await ctx.reply(embed=discord.Embed(title='Пауза!',
                                                      colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                                    random.randrange(0, 255),
                                                                                    random.randrange(0, 255))),
                                  mention_author=False)
            await mes.add_reaction('✅')
        except Exception:
            await ctx.reply('ALARM!ALARM! ВОЗНИКЛА ОШИБКА! ALARM!ALARM!', mention_author=False)
            return

    @commands.command(name='resume')
    async def resume(self, ctx):
        try:
            try:
                vc = ctx.guild.voice_client
            except Exception:
                ctx.reply('Ну сам-то зайди тоже', mention_author=False)
            vc.resume()
            mes = await ctx.reply(embed=discord.Embed(title='Воспроизведение продолжается!',
                                                      colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                                    random.randrange(0, 255),
                                                                                    random.randrange(0, 255))),
                                  mention_author=False)
            await mes.add_reaction('✅')
        except Exception:
            await ctx.reply('ALARM!ALARM! ВОЗНИКЛА ОШИБКА! ALARM!ALARM!', mention_author=False)
            return

    @commands.command(name='back', aliases=['b'])
    async def back(self, ctx):
        global queues_n, queues, prev, prev_n, now
        if ctx.message.guild.id in is_potok:
            if is_potok[ctx.message.guild.id] is True:
                embed = discord.Embed(title='Недоступно во время потока(',
                                      colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                    random.randrange(0, 255),
                                                                    random.randrange(0, 255)))
                mes = await ctx.reply(embed=embed, mention_author=False)
                await mes.add_reaction('❌')
                return
        id = ctx.message.guild.id
        try:
            a = easy_convert(prev_n[id])[0]
        except KeyError:
            a = easy_convert('rick astley - never gonna give you up')[0]
        b = prev_n[id]
        try:
            sss = easy_convert(prev_n[id])[-1]
        except Exception as e:
            await ctx.reply(discord.Embed(title='Ошибка воспроизведения:',
                                          colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                        random.randrange(0, 255),
                                                                        random.randrange(0, 255)),
                                          description=str(e)), mention_author=False)
        if int(sss['duration']) > 60:
            m = int(sss['duration']) // 60
            s = int(sss['duration']) - int(sss['duration']) // 60 * 60
            if m > 60:
                ch = m // 60
                ost_m = m - ch * 60
                queues_n[id].append(
                    sss['title'] + ' --- ' + str(ch) + ' ч. ' + str(ost_m) + ' м. ' + str(s) + ' c.')
            else:
                queues_n[id].append(sss['title'] + ' --- ' + str(m) + ' м. ' + str(s) + ' c.')

        else:
            queues_n[id].append(sss['title'] + ' --- ' + str(sss['duration']) + ' c.')
        if len(queues[id]) >= 1:
            queues[id] = [a] + [easy_convert(now[id])[0]] + queues[id][:-1]
            queues_n[id] = [b] + [now[id]] + queues_n[id][:-1]
            print('------------------------------------------------')
        else:
            queues[id] = [a]
            queues_n[id] = [b]
        prev[id] = easy_convert(now[id])[0]
        prev_n[id] = now[id]
        print(prev_n[id])
        vc.stop()
        check_queue(ctx, id)

    @commands.command(name='we')
    async def we(self, ctx):
        global sl_weather
        try:
            if ctx.message.content.split('-we')[-1] and ctx.message.content.split('-we')[-1] != ' ':
                n = ctx.message.content.split('-we ')[-1].strip()
                x, y = requests.get(
                    f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={n}&format=json").json()[
                    "response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"].split()
                res = yandex_weather_api.get(requests, '5a57c893-985b-482d-a875-1f09c7151960', lat=y, lon=x)
                embed = discord.Embed(title='Погода',
                                      description=f'Температура: {str(res["fact"]["temp"])}°С\nОщущается как: {str(res["fact"]["feels_like"])}°С\nПогодные условия: {sl_weather[str(res["fact"]["condition"])][0]}\nВлажность: {str(res["fact"]["humidity"]) + "%"}\nСкорость ветра: {str(res["fact"]["wind_speed"]) + " М/С"}',
                                      colour=0x9999FF)
                embed.set_author(name='Яндекс.Погода',
                                 icon_url=f'https://yastatic.net/s3/home-static/_/37/37a02b5dc7a51abac55d8a5b6c865f0e.png')
                embed.set_image(url=sl_weather[str(res["fact"]["condition"])][-1])
                await ctx.reply(embed=embed, mention_author=False)
            else:
                await ctx.reply('Ну ты город-то введи', mention_author=False)
        except Exception:
            await ctx.reply('Команда -we не сработала(((', mention_author=False)

    @commands.command(name='filt', aliases=['filter', 'f', 'ашдеук', 'а'])
    async def filt(self, ctx):
        try:
            img = Image.open(requests.get(ctx.message.attachments[0].url, stream=True).raw)
            img.save('example.png')
            #if ctx.message.content.split()[1] == 'dem':
            #    if ';' in ctx.message.content:
            #        dem = Demotivator(ctx.message.content.split('-filter dem')[-1].split(';')[0],
            #                          ctx.message.content.split('-filter dem')[-1].split(';')[-1])
            #    else:
            #        dem = Demotivator(ctx.message.content.split('-filter dem')[-1], '')
            #    dem.create("example.png", result_filename='bebra.png')
            #    await ctx.reply(file=discord.File('bebra.png'), mention_author=False)
            elif ctx.message.content.split()[1] == 'ascii':
                width = int(ctx.message.content.split()[2])
                height_scale = 0.6
                org_width, orig_height = img.size
                aspect_ratio = orig_height / org_width
                new_height = aspect_ratio * width * height_scale
                img = img.resize((width, int(new_height)))
                img = img.convert('RGBA')
                img = ImageEnhance.Sharpness(img).enhance(2.0)
                pixels = img.getdata()

                def mapto(r, g, b, alpha):
                    if alpha == 0.:
                        return ' '
                    chars = ["B", "S", "#", "&", "@", "$", "%", "*", "!", ".", " "]
                    chars.reverse()
                    pixel = (r * 19595 + g * 38470 + b * 7471 + 0x8000) >> 16
                    return chars[pixel // 25]

                new_pixels = [mapto(r, g, b, alpha) for r, g, b, alpha in pixels]
                new_pixels_count = len(new_pixels)
                ascii_image = [''.join(new_pixels[index:index + width]) for index in range(0, new_pixels_count, width)]
                ascii_image = "\n".join(ascii_image)
                with open("bebra.txt", "w") as file:
                    file.write(ascii_image)
                await ctx.reply(file=discord.File("bebra.txt"), mention_author=False)
                os.remove('bebra.txt')
            elif ctx.message.content.split()[1] == 'b-w':
                img = img.convert('L')
                img.save('bebra.png')
                await ctx.reply(file=discord.File('bebra.png'), mention_author=False)
            elif ctx.message.content.split()[1] == 'quantize':
                img = img.quantize(10)
                img.save('bebra.png')
                await ctx.reply(file=discord.File('bebra.png'), mention_author=False)
            elif ctx.message.content.split()[1] == 'blur':
                img = img.filter(ImageFilter.GaussianBlur(radius=2))
                img.save('bebra.png')
                await ctx.reply(file=discord.File('bebra.png'), mention_author=False)
            elif ctx.message.content.split()[1] == 'negative':
                img = ImageOps.invert(img)
                img.save('bebra.png')
                await ctx.reply(file=discord.File('bebra.png'), mention_author=False)
            #elif ctx.message.content.split()[1] == 'cit':
            #    if len(ctx.message.content.split('-filter cit ')[-1].split(';')) == 2:
            #        a = Quote(ctx.message.content.split('-filter cit ')[-1].split(';')[0],
            #                  ctx.message.content.split('-filter cit ')[-1].split(';')[-1])
            #    else:
            #        a = Quote(ctx.message.content.split('-filter cit ')[-1].split(';')[0], 'неизвестный мыслитель')
            #    a.create("example.png", result_filename='bebra.png')
            #    await ctx.reply(file=discord.File('bebra.png'), mention_author=False)
            elif ctx.message.content.split()[1] == 'sh' or ctx.message.content.split()[1] == 'shakal':
                if img.size[0] > 2000 or img.size[-1] > 2000:
                    img = img.resize((int(img.size[0] * 0.5), int(img.size[-1] * 0.5)))
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(600)
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(0.85)
                img.save('bebra.png')
                await ctx.reply(file=discord.File('bebra.png'), mention_author=False)
            try:
                os.remove('bebra.png')
                os.remove('example.png')
            except Exception:
                pass
        except ValueError:
            await ctx.reply('Здесь не RGB! Прошу поменять формат', mention_author=False)

    @commands.command(name='h')
    async def help(self, ctx):
        embed = discord.Embed(title='Все команды бота:', colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                                       random.randrange(0, 255),
                                                                                       random.randrange(0, 255)))
        embed.add_field(name="-hello", value='Скажет "Привет";', inline=False)
        embed.add_field(name="-p или -pl (желаемая песня)", value="""Включит в вашем голосовом канале
             желаемую музыку;""", inline=False)
        embed.add_field(name="-play (желаемая песня)", value="""Включит в вашем голосовом канале
                     желаемую музыку, не обращая внимания на очередь;""", inline=False)
        embed.add_field(name="-stream/potok (желаемая песня)", value="""Включит в вашем голосовом канале бесконечную
         подборку музыки, основанную на вашем запросе;""", inline=False)
        embed.add_field(name="-stop", value="""Выключит действующий поток;""", inline=False)
        embed.add_field(name="-lyrics", value="""Вышлет текст песни, играющей сейчас;""", inline=False)
        embed.add_field(name="-clear или -c", value="Очищает очередь из музыки;", inline=False)
        embed.add_field(name="-queue или -q", value="Покажет текущую очередь из песен;", inline=False)
        embed.add_field(name="-skip или -s", value="Пропускает музыку, которая идет сейчас;", inline=False)
        embed.add_field(name="-leave или -l", value="Покидает голосовой канал;", inline=False)
        embed.add_field(name="-cz/ttt", value="""Запускает партию в крестики-нолики с гениальным ИИ, 
            которого вы никогда не победите;""", inline=False)
        embed.add_field(name="-mem (число)", value="Выдает шаблон для мема;", inline=False)
        embed.add_field(name="-getmem", value="Выдает случайный мем с реддита;", inline=False)
        embed.add_field(name="-mem_h (число страницы)", value="Выдает список самых популярных шаблонов для мемов;",
                        inline=False)
        embed.add_field(name="-wiki (ваш запрос)", value="Выдает краткую информацию о том, что вы ищете, из Википедии;",
                        inline=False)
        embed.add_field(name="-we (город или населенный пункт)", value="""Присылает текущее состояние погоды
             в вашем городе или населенном пункте;""", inline=False)
        embed.add_field(name="-rofl_h", value="Помощь по рофлам;", inline=False)
        embed.add_field(name="-rofl (число, обозначающее тип рофла)", value="""Присылает рофлянку введенной
             категории (-rofl_h);""", inline=False)
        embed.add_field(name="-filter (вид эффекта) + ваша фотография", value="""Присылает обработанную фотографию
         по фильтру, ввыбранному вами из списка (-filter_h).""", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='filter_h')
    async def filter_h(self, ctx):
        embed = discord.Embed(title='Фотообработчики бота:', colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                                           random.randrange(0, 255),
                                                                                           random.randrange(0, 255)))
        embed.add_field(name="dem (текст1);(текст2)", value='Создаст демотиватор;', inline=False)
        embed.add_field(name="b-w", value='Создаст черно-белую фотографию;', inline=False)
        embed.add_field(name="quantize", value='Создаст отквантованную фотографию;', inline=False)
        embed.add_field(name="blur", value="Создаст размытую фотографию;", inline=False)
        embed.add_field(name="negative", value="Инвертирует цвета на фотографии;", inline=False)
        embed.add_field(name="cit (текст);(автор)", value="Создает цитату;", inline=False)
        embed.add_field(name="sh или shakal", value="Сильно повышает резкость изображения;", inline=False)
        embed.add_field(name="ascii (желаемая ширина изображения в символах)",
                        value="Конвертирует вашу фотографию в текстовый формат по символам таблицы ASCII.",
                        inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=['pl'])
    async def p(self, ctx):
        global vc, url, ydl, queues_n, queues, is_potok
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
        guild_id = ctx.message.guild.id
        try:
            if guild_id in is_potok:
                if is_potok[guild_id] is True:
                    embed = discord.Embed(title="Ошибка воспроизведения:",
                                          description='Недоступно во время потока(',
                                          colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                        random.randrange(0, 255),
                                                                        random.randrange(0, 255)))
                    mes = await ctx.reply(embed=embed, mention_author=False)
                    await mes.add_reaction('❌')
                    return
            ydl.cache.remove()
            if 'https://' in url:
                info = ydl.extract_info(url, download=False)
            else:
                info = ydl.extract_info(f"ytsearch:{url}", download=False)['entries'][0]
            if not info:
                embed = discord.Embed(title="Ошибка воспроизведения:",
                                      description='Отказано в доступе к сервису;\nПопробуйте еще раз!',
                                      colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                    random.randrange(0, 255),
                                                                    random.randrange(0, 255)))
                mes = await ctx.reply(embed=embed, mention_author=False)
                await mes.add_reaction('❌')
                return
        except Exception as e:
            embed = discord.Embed(title="Ошибка воспроизведения:",
                                  description=e,
                                  colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                random.randrange(0, 255),
                                                                random.randrange(0, 255)))
            mes = await ctx.reply(embed=embed, mention_author=False)
            await mes.add_reaction('❌')
            return
        arg = info['formats'][0]['url']
        if guild_id not in queues_n:
            queues_n[guild_id] = []
        if vc.is_paused() or vc.is_playing():
            b = info
            if guild_id in queues:
                queues[guild_id].append((FFmpegPCMAudio(executable=ffmpeg, source=arg, **FFMPEG_OPTIONS)))
            else:
                queues[guild_id] = [(FFmpegPCMAudio(executable=ffmpeg, source=arg, **FFMPEG_OPTIONS))]
            embed = discord.Embed(title="Добавлено в очередь:", url=b['webpage_url'],
                                  description=b['title'],
                                  colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                random.randrange(0, 255),
                                                                random.randrange(0, 255)))
            embed.set_author(name=b['uploader'])
            embed.set_thumbnail(url=b['thumbnails'][-1]['url'])
            if int(b['duration']) > 60:
                m = int(b['duration']) // 60
                s = int(b['duration']) - int(b['duration']) // 60 * 60
                if m > 60:
                    ch = m // 60
                    ost_m = m - ch * 60
                    embed.add_field(name="Длительность: ",
                                    value='`' + str(ch) + ' ч. ' + str(ost_m) + ' м. ' + str(s) + ' c.`')
                    queues_n[guild_id].append(
                        b['title'] + ' --- ' + str(ch) + ' ч. ' + str(ost_m) + ' м. ' + str(s) + ' c.')
                else:
                    embed.add_field(name="Длительность: ",
                                    value='`' + str(m) + ' м. ' + str(s) + ' c.`')
                    queues_n[guild_id].append(b['title'] + ' --- ' + str(m) + ' м. ' + str(s) + ' c.')

            else:
                embed.add_field(name="Длительность: ",
                                value='`' + str(b['duration']) + ' c.`')
                queues_n[guild_id].append(b['title'] + ' --- ' + str(b['duration']) + ' c.')
            mes = await ctx.reply(embed=embed, mention_author=False)
            await mes.add_reaction('✅')
        else:
            b = info
            if int(b['duration']) > 60:
                m = int(b['duration']) // 60
                s = int(b['duration']) - int(b['duration']) // 60 * 60
                if m > 60:
                    ch = m // 60
                    ost_m = m - ch * 60
                    queues_n[guild_id].append(
                        b['title'] + ' --- ' + str(ch) + ' ч. ' + str(ost_m) + ' м. ' + str(s) + ' c.')
                else:
                    queues_n[guild_id].append(b['title'] + ' --- ' + str(m) + ' м. ' + str(s) + ' c.')
            else:
                queues_n[guild_id].append(b['title'] + ' --- ' + str(b['duration']) + ' c.')
            if guild_id in queues:
                queues[guild_id].append((FFmpegPCMAudio(executable=ffmpeg, source=arg, **FFMPEG_OPTIONS)))
            else:
                queues[guild_id] = [(FFmpegPCMAudio(executable=ffmpeg, source=arg, **FFMPEG_OPTIONS))]
            check_queue(ctx, guild_id)

    @commands.command(aliases=['pot', 'str', 'stream', 'wave', 'wv'])
    async def potok(self, ctx):
        global vc, url, ydl, queues_n, queues, is_potok
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
        try:
            ydl.cache.remove()
            if 'https://' in url:
                info = ydl.extract_info(url, download=False)
            else:
                info = ydl.extract_info(f"ytsearch:{url}", download=False)['entries'][0]
                url = ydl.extract_info(f"ytsearch:{url}", download=False)['entries'][0]['webpage_url']
            if not info:
                embed = discord.Embed(title="Ошибка воспроизведения:",
                                      description='Отказано в доступе к сервису;\nПопробуйте еще раз!',
                                      colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                    random.randrange(0, 255),
                                                                    random.randrange(0, 255)))
                mes = await ctx.reply(embed=embed, mention_author=False)
                await mes.add_reaction('❌')
                return
        except Exception as e:
            embed = discord.Embed(title="Ошибка воспроизведения:",
                                  description=e,
                                  colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                random.randrange(0, 255),
                                                                random.randrange(0, 255)))
            mes = await ctx.reply(embed=embed, mention_author=False)
            await mes.add_reaction('❌')
            return
        guild_id = ctx.message.guild.id
        if vc.is_paused() or vc.is_playing():
            embed = discord.Embed(title="Ошибка воспроизведения:",
                                  description="Невозможно инициализировать поток, пока ваша очередь непуста",
                                  colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                random.randrange(0, 255),
                                                                random.randrange(0, 255)))
            mes = await ctx.reply(embed=embed, mention_author=False)
            await mes.add_reaction('❌')
            return
        else:
            embed = discord.Embed(title="Успех! Приятного прослушивания",
                                  description="(Функция находится в стадии разработки!!!)",
                                  colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                random.randrange(0, 255),
                                                                random.randrange(0, 255)))
            await ctx.reply(embed=embed, mention_author=False)
            is_potok[guild_id] = True
            check_potok(ctx, url, info, guild_id)

    @commands.command()
    async def play(self, ctx):
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
        guild_id = ctx.message.guild.id
        try:
            if guild_id in is_potok:
                if is_potok[guild_id] is True:
                    embed = discord.Embed(title="Ошибка воспроизведения:",
                                          description='Недоступно во время потока(',
                                          colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                        random.randrange(0, 255),
                                                                        random.randrange(0, 255)))
                    mes = await ctx.reply(embed=embed, mention_author=False)
                    await mes.add_reaction('❌')
                    return
            ydl.cache.remove()
            if 'https://' in url:
                info = ydl.extract_info(url, download=False)
            else:
                info = ydl.extract_info(f"ytsearch:{url}", download=False)['entries'][0]
            if info is None:
                embed = discord.Embed(title="Ошибка воспроизведения:",
                                      description='Отказано в доступе к сервису;\nПопробуйте еще раз!',
                                      colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                    random.randrange(0, 255),
                                                                    random.randrange(0, 255)))
                mes = await ctx.reply(embed=embed, mention_author=False)
                await mes.add_reaction('❌')
                return
        except Exception as e:
            embed = discord.Embed(title="Ошибка воспроизведения:",
                                  description=e,
                                  colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                random.randrange(0, 255),
                                                                random.randrange(0, 255)))
            mes = await ctx.reply(embed=embed, mention_author=False)
            await mes.add_reaction('❌')
            return
        arg = info['formats'][0]['url']
        if guild_id not in queues_n:
            queues_n[guild_id] = []
        b = info
        if guild_id in queues:
            queues[guild_id] = [(FFmpegPCMAudio(executable=ffmpeg, source=arg, **FFMPEG_OPTIONS))] + \
                               queues[guild_id]
        else:
            queues[guild_id] = [(FFmpegPCMAudio(executable=ffmpeg, source=arg, **FFMPEG_OPTIONS))]
        if int(b['duration']) > 60:
            m = int(b['duration']) // 60
            s = int(b['duration']) - int(b['duration']) // 60 * 60
            if m > 60:
                ch = m // 60
                ost_m = m - ch * 60
                if guild_id in queues_n:
                    queues_n[guild_id] = [(b['title'] + ' --- ' + str(ch) + ' ч. ' + str(ost_m) + ' м. ' + str(
                        s) + ' c.')] \
                                         + queues_n[guild_id]
                else:
                    queues_n[guild_id] = [
                        (b['title'] + ' --- ' + str(ch) + ' ч. ' + str(ost_m) + ' м. ' + str(s) + ' c.')]
            else:
                if guild_id in queues_n:
                    queues_n[guild_id] = [(b['title'] + ' --- ' + str(m) + ' м. ' + str(s) + ' c.')] + queues_n[
                        guild_id]
                else:
                    queues_n[guild_id] = [(b['title'] + ' --- ' + str(m) + ' м. ' + str(s) + ' c.')]
        else:
            if guild_id in queues_n:
                queues_n[guild_id] = [(b['title'] + ' --- ' + str(b['duration']) + ' c.')] + queues_n[guild_id]
            else:
                queues_n[guild_id] = [(b['title'] + ' --- ' + str(b['duration']) + ' c.')]
        if vc.is_playing():
            vc.stop()
        else:
            check_queue(ctx, guild_id)

    @commands.command(aliases=['c', 'с'])
    async def clear(self, ctx):
        global queues, queues_n
        connected = ctx.author.voice
        if not connected:
            await ctx.reply("Ну сам-то зайди тоже", mention_author=False)
            return
        queues = {}
        queues_n = {}
        embed = discord.Embed(title="Очередь была полностью очищена!",
                              colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                            random.randrange(0, 255),
                                                            random.randrange(0, 255)))
        mes = await ctx.reply(embed=embed, mention_author=False)
        await mes.add_reaction('✅')

    @commands.command()
    async def stop(self, ctx):
        global is_potok
        connected = ctx.author.voice
        if not connected:
            await ctx.reply("Ну сам-то зайди тоже", mention_author=False)
            return
        is_potok[ctx.message.guild.id] = False
        vc.stop()
        embed = discord.Embed(title="Поток успешно остановлен. Захади еще!",
                              colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                            random.randrange(0, 255),
                                                            random.randrange(0, 255)))
        mes = await ctx.reply(embed=embed, mention_author=False)
        await mes.add_reaction('✅')

    @commands.command(aliases=['s', 'ы'])
    async def skip(self, ctx):
        try:
            global queues, now
            connected = ctx.author.voice
            if not connected:
                await ctx.reply("Ну сам-то зайди тоже", mention_author=False)
                return
            vc = ctx.guild.voice_client
            if ctx.message.guild.id in is_potok:
                if is_potok[ctx.message.guild.id] is True:
                    vc.stop()
                    embed = discord.Embed(title="Песня была успешно пропущена!",
                                          description=now[ctx.message.guild.id],
                                          colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                        random.randrange(0, 255),
                                                                        random.randrange(0, 255)))
                    mes = await ctx.reply(embed=embed, mention_author=False)
                    await mes.add_reaction('✅')
                    return
            if vc.is_playing():
                vc.stop()
                if queues:
                    embed = discord.Embed(title="Песня была успешно пропущена!",
                                          description=now[ctx.message.guild.id],
                                          colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                        random.randrange(0, 255),
                                                                        random.randrange(0, 255)))
                    mes = await ctx.reply(embed=embed, mention_author=False)
                    await mes.add_reaction('✅')
            elif vc.is_paused():
                vc.resume()
                vc.stop()
                if queues:
                    embed = discord.Embed(title="Песня была успешно пропущена!",
                                          description=now[ctx.message.guild.id],
                                          colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                        random.randrange(0, 255),
                                                                        random.randrange(0, 255)))
                    mes = await ctx.reply(embed=embed, mention_author=False)
                    await mes.add_reaction('✅')
        except IndexError:
            pass

    @commands.command(aliases=['q', 'й'])
    async def queue(self, ctx):
        global queues_n, queues, now
        if ctx.message.guild.id in is_potok:
            if is_potok[ctx.message.guild.id] is True:
                embed = discord.Embed(title='Недоступно во время потока(',
                                      colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                    random.randrange(0, 255),
                                                                    random.randrange(0, 255)))
                mes = await ctx.reply(embed=embed, mention_author=False)
                await mes.add_reaction('❌')
                return
        id = ctx.message.guild.id
        if id in queues and (vc.is_playing() or vc.is_paused()):
            q = queues_n[ctx.message.guild.id]
            embed = discord.Embed(title='Текущая очередь из песен:',
                                  colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                random.randrange(0, 255),
                                                                random.randrange(0, 255)))
            embed.add_field(name='Играет прямо сейчас:', value=now[ctx.message.guild.id], inline=False)
            for i, e in enumerate(q):
                embed.add_field(name=str(i + 1) + ' - ', value=e, inline=False)
            mes = await ctx.reply(embed=embed, mention_author=False)
            await mes.add_reaction('✅')
        else:
            embed = discord.Embed(title='Показывать нечего', colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                                           random.randrange(0, 255),
                                                                                           random.randrange(0, 255)))
            mes = await ctx.reply(embed=embed, mention_author=False)
            await mes.add_reaction('✅')

    @commands.command(aliases=['l', 'д'])
    async def leave(self, ctx):
        connected = ctx.author.voice
        if not connected:
            await ctx.reply("Ну сам-то зайди тоже", mention_author=False)
            return
        if ctx.voice_client:
            id = ctx.message.guild.id
            await ctx.voice_client.disconnect()
            mes = await ctx.reply('Ладно, я пошел. До связи', mention_author=False)
            await mes.add_reaction('😭')
            prev_n[id] = []
            prev[id] = []
            queues_n[id] = []
            queues[id] = []
            now[id] = []
        else:
            await ctx.reply('Да я и не подключен вроде', mention_author=False)

    @commands.command(name='mem')
    async def mem(self, ctx):
        try:
            if len(ctx.message.content.split()) == 2:
                n = int(ctx.message.content.split()[-1]) - 1
                res = (requests.get('https://api.imgflip.com/get_memes')).json()
                mem = res['data']['memes'][n]['url']
                await ctx.reply(mem, mention_author=False)
            else:
                n = int(ctx.message.content.split()[1]) - 1
                spn = ' '.join(ctx.message.content.split()[2:]).split(';')
                if len(spn) == int(
                        (requests.get('https://api.imgflip.com/get_memes')).json()['data']['memes'][n]['box_count']):
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
                    await ctx.reply(
                        "Для создания мема необходимо, чтобы кол-во полей в меме совпадало с кол-вом введенных подписей. Перепроверь данные",
                        mention_author=False)
        except Exception:
            await ctx.reply('Видимо, ты забыл написать цифру после команды или же просто допустил ошибку(',
                            mention_author=False)

    @commands.command(name='getmem')
    async def getmem(self, ctx):
        try:
            if len(ctx.message.content.split()) == 1:
                res = (requests.get('https://meme-api.herokuapp.com/gimme')).json()
                mem = res['url']
                await ctx.reply(mem, mention_author=False)
            else:
                await ctx.reply('Видимо, ты лишка чего-то понавыписывал(', mention_author=False)
        except Exception:
            await ctx.reply('ALARM!ALARM! ВОЗНИКЛА ОШИБКА! ALARM!ALARM!', mention_author=False)
            return

    @commands.command(name='mem_h')
    async def mem_h(self, ctx):
        try:
            n = int(ctx.message.content.split()[-1]) - 1
            res = (requests.get('https://api.imgflip.com/get_memes')).json()
            embed = discord.Embed(title='Текущий "топ" мемов:',
                                  description=':white_check_mark: - подходит для создания мема\n :x: - не подходит',
                                  colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                random.randrange(0, 255),
                                                                random.randrange(0, 255)))
            c = 1
            for i, e in enumerate(res['data']['memes']):
                if (i + 1 >= n * 10) and (i + 1 <= n * 10 + 10):
                    if e['box_count'] > 2:
                        embed.add_field(name=str(c) + '. ',
                                        value=e['name'] + ' | ' + 'Кол-во полей: ' + str(e['box_count']) + ' | :x:',
                                        inline=False)
                    else:
                        embed.add_field(name=str(c) + '. ',
                                        value=e['name'] + ' | ' + 'Кол-во полей: ' + str(
                                            e['box_count']) + ' | :white_check_mark:',
                                        inline=False)
                c += 1
            await ctx.reply(embed=embed, mention_author=False)
        except Exception:
            await ctx.reply('Возможно, ты забыл написать цифру-номер страницы', mention_author=False)

    @commands.command(name='rofl_h')
    async def rofl_h(self, ctx):
        try:
            embed = discord.Embed(title="Список команд для -rofl:", description="""
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
                        14 - Статусы (+18).""", colour=discord.Color.from_rgb(random.randrange(0, 255),
                                                                              random.randrange(0, 255),
                                                                              random.randrange(0, 255)))
            await ctx.reply(embed=embed, mention_author=False)
        except Exception:
            await ctx.reply('Команда rofl_h не сработала(((', mention_author=False)

    @commands.command(name='rofl')
    async def rofl(self, ctx):
        try:
            sl = {'1': '1',
                  '2': '2',
                  '3': '3',
                  '4': '4',
                  '5': '5',
                  '6': '6',
                  '7': '8',
                  '8': '11',
                  '9': '12',
                  '10': '13',
                  '11': '14',
                  '12': '15',
                  '13': '16',
                  '14': '18', }
            n = ctx.message.content.split('-rofl ')[-1].strip()
            n = sl[n]
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
            await ctx.reply('Категории смешнявок можно изучить, вызвав команду -rofl_h', mention_author=False)


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    bot.add_cog(Speedwagon(bot))
    bot.run(os.environ['TOKEN'])
