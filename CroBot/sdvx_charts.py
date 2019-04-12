# TODO: MASSIVE GOALS:
# TODO:                CLEAN UP THIS SPAGHETTI
# TODO:                MODULARIZE IT


import os
import re
import random
import requests

from datetime import datetime

from googletrans import Translator
from unidecode import unidecode
import html.parser

from fuzzywuzzy import fuzz
import asyncio

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker


from CroBot.features.sdvxin.song import Song

# Database setup

base = declarative_base()
class Chart(base):
    __tablename__ = 'charts'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    name_romanized = Column(String)
    name_romanized_no_space = Column(String)
    name_translated = Column(String)
    artist = Column(String)
    song_id = Column(String)

    link_nov = Column(String)
    link_adv = Column(String)
    link_exh = Column(String)
    link_max = Column(String)

    link_video_play = Column(String)
    link_video_nfx = Column(String)
    link_video_og = Column(String)
    link_jacket = Column(String)

    diff_nov = Column(Integer)
    diff_adv = Column(Integer)
    diff_exh = Column(Integer)
    diff_max = Column(Integer)
    diff_max_type = Column(Integer)


engine = create_engine('sqlite:///sdvxCharts.db')
session_maker = sessionmaker(bind=engine)

# Initial DB set up; type 0 is rebuild ; type 1 is update
async def init(session, type):
    print('Starting database entry')

    sort_list = ['http://sdvx.in/sort/sort_a.js', 'http://sdvx.in/sort/sort_k.js', 'http://sdvx.in/sort/sort_s.js',
                'http://sdvx.in/sort/sort_t.js', 'http://sdvx.in/sort/sort_n.js', 'http://sdvx.in/sort/sort_h.js',
                'http://sdvx.in/sort/sort_m.js', 'http://sdvx.in/sort/sort_y.js', 'http://sdvx.in/sort/sort_r.js',
                'http://sdvx.in/sort/sort_w.js', 'http://sdvx.in/files/del.js']

    # sort_list = ['http://www.sdvx.in/sort/sort_19.js'] # Used for testing

    # name list for update
    name_list = []
    # To check for specific song updates
    partial = False

    # If a general update
    if type == None:
        # If only one query field, it will be formatted as ('songname',)
        for id, s_id in session.query(Chart.id, Chart.song_id):
            name_list.append(s_id)

    # For specific song update
    elif int(type) > 1000:
        name_list = [type]
        partial = True

    for item in sort_list:
        await parse_sort(item, session, 2 if partial else type, name_list)
        await asyncio.sleep(1)


async def parse_sort(url, session, type, name_list):
    print('Parsing '+ url)
    try:
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None, requests.get, url)
        future_result = await future
        req = future_result.text.split('\n')
        regex = r'(/\d.*js)'

        if type == 0:
            # Sift through the sort js file to get the urls of the charts
            for line in req:
                if re.search(regex, line) is not None:
                    parse = re.search(regex, line).group(1)
                    song_id = re.search(r'/(\d+)sort.js', line).group(1)
                    await parse_chart('http://sdvx.in' + parse, session, song_id)

        elif type is None:
            for line in req:
                if re.search(regex, line) is not None and re.search(r'/(\d+)sort.js', line).group(1) not in name_list:
                    parse = re.search(regex, line).group(1)
                    song_id = re.search(r'/(\d+)sort.js', line).group(1)
                    await parse_chart('http://sdvx.in' + parse, session, song_id)

        else:
            for line in req:
                if re.search(regex, line) is not None and re.search(r'/(\d+)sort.js', line).group(1) in name_list:
                    parse = re.search(regex, line).group(1)
                    song_id = re.search(r'/(\d+)sort.js', line).group(1)
                    await parse_chart('http://sdvx.in' + parse, session, song_id)

    except Exception as e:
        print(str(e) + ': failure on ' + url)

# todo: normalize variable names
# Regex to be used for parse_chart
name_regex = r'(\d+)\s+(.+)' # Group 1 is sdvx.in's id for the song; Group 2 is the song name
artist_regex = r'ARTIST\d*.*2>.*/\s(.*)<'
sort_regex = r'SORT\d*' # Used to filter out the sort line
dif_regex = r'LV\d+[NAEIGHM]'
nov_regex = r'LV\d+N'
adv_regex = r'LV\d+A'
exh_regex = r'LV\d+E'
max_regex = r'LV\d+[IGHM]'
link_regex = r'/\d.*htm'
difficulty_regex = r'(\d+)</div>'
jacket_regex = r'(/\d+/jacket/\d+[em]....)'
jp_regex = r'[\u3000-\u303F]|[\u3040-\u309F]|[\u30A0-\u30FF]|[\uFF00-\uFFEF]|[\u4E00-\u9FAF]|[\u2605-\u2606]|[\u2190-\u2195]|\u203B' # https://gist.github.com/sym3tri/980083
video_regex = r'SD\d+[FO]'
video_p_regex = r'MV\d+[EIGHM]'
v_nfx_regex = r'SD\d+F'
v_og_regex = r'SD\d+O'
v_link_regex = r'href=(\S+youtube\S+)'


async def parse_chart(url, session, song_id):
    print('Parsing ' + url)
    try:
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None, requests.get, url)
        futureResult = await future
        req = futureResult.text.split('\n')

        # Sift through the chart js file to get information
        name, name_trans, rom, rom_pronunciation, art, link_n, link_a, link_e, link_m, dif_n, dif_a, dif_e, dif_m, jacket, v_p, v_nfx, v_og = (None,)*17
        mDif = 0
        for i, line in enumerate(req):
            # If the line contains a difficulty link
            if re.search(dif_regex, line) is not None and re.search(sort_regex, line) is None:
                # If line has nov difficulty
                if re.search(nov_regex, line) is not None:
                    link_n = 'http://sdvx.in' + re.search(link_regex, line).group(0)
                    dif_n = re.search(difficulty_regex, line).group(1)
                # If line has adv difficulty
                elif re.search(adv_regex, line) is not None:
                    link_a = 'http://sdvx.in' + re.search(link_regex, line).group(0)
                    dif_a = re.search(difficulty_regex, line).group(1)
                # If line has exh difficulty
                elif re.search(exh_regex, line) is not None:
                    link_e = 'http://sdvx.in' + re.search(link_regex, line).group(0)
                    dif_e = re.search(difficulty_regex, line).group(1)
                # If line has max difficulty
                elif re.search(max_regex, line) is not None:
                    link_m = 'http://sdvx.in' + re.search(link_regex, line).group(0)
                    dif_m = re.search(difficulty_regex, line).group(1)
                    # Set difficulty value
                    if 'I' in line:
                        mDif = 1
                    elif 'G' in line:
                        mDif = 2
                    elif 'H' in line:
                        mDif = 3
                    elif 'M' in line:
                        mDif = 4

            # If video line
            elif re.search(video_regex, line) is not None:
                if re.search(v_nfx_regex, line) is not None and re.search(v_link_regex, line) is not None:
                    v_nfx = re.search(v_link_regex, line).group(1)
                elif re.search(v_og_regex, line) is not None  and re.search(v_link_regex, line) is not None:
                    v_og = re.search(v_link_regex, line).group(1)

            # If playing video line
            elif re.search(video_p_regex, line) is not None:
                if re.search(v_link_regex, line) is not None:
                    v_p = re.search(v_link_regex, line).group(1)

            # If artist line
            elif re.search(artist_regex, line) is not None:
                art = html.unescape(re.search(artist_regex, line).group(1))

            # If first line
            elif i == 0:
                # Get name of the song and removes any html tags
                name = re.sub(r'<[^<]+?>', '', html.unescape(re.search(name_regex, line).group(2)))

                # Get romanized jp title

                # Only toss to google if it contains jp
                if re.search(jp_regex, name) is not None:
                    future_nt = loop.run_in_executor(None, lambda: Translator().translate(name, src='ja', dest='en'))
                    future_p = loop.run_in_executor(None, lambda: Translator().translate(name, dest='ja'))
                    future_nt_result = await future_nt
                    future_p_result = await future_p
                    name_trans = future_nt_result.text
                    rom_pronunciation = future_p_result.pronunciation

                # If received jp from google, save as rom - decoded without pronunciation guides
                if rom_pronunciation is not None:
                    rom = unidecode(rom_pronunciation)

                # If nothing received from google, assume no jp and save title as rom
                else:
                    name_trans = name
                    rom = name

        romNS = rom.replace(' ', '')

        # Gets jacket art
        future2 = loop.run_in_executor(None, requests.get, url.replace('sort', 'data'))
        future_result2 = await future2
        req2 = future_result2.text.split('\n')
        for line in req2:
            if re.search(jacket_regex, line) is not None:
                jacket = 'http://sdvx.in'+re.search(jacket_regex, line).group(1)

        await add_to_db(name, rom, romNS, name_trans, art, song_id, link_n, link_a, link_e, link_m,
                        dif_n, dif_a, dif_e, dif_m, mDif, jacket, v_p, v_nfx, v_og, session)

    except Exception as e:
        print(str(e)+': failure on '+url)


async def add_to_db(name, rom, rom_ns, name_trans, art, song_id, link_n, link_a, link_e, link_m,
                    dif_n, dif_a, dif_e, dif_m, m_dif, jacket, v_p, v_nfx, v_og, session):
    # Check if it already exists, if it does update it
    search_list = await query(song_id)
    if len(search_list) == 1 and search_list[0].song_id == song_id:
        data = {'name': name, 'name_romanized': rom, 'name_rom_no_space': rom_ns, 'name_translated': name_trans, 'artist': art,
                'song_id': song_id, 'link_nov': link_n, 'link_adv': link_a, 'link_exh': link_e, 'link_max': link_m,
                'dif_nov': dif_n, 'dif_adv': dif_a, 'dif_exh': dif_e, 'dif_max': dif_m, 'max_dif': m_dif,
                'jacket': jacket, 'video_play': v_p, 'video_nfx': v_nfx, 'video_og': v_og}
        session.query(Chart).filter_by(song_id=search_list[0].song_id).update(data)

    else:
        session.add(Chart(name=name, name_romanized=rom, name_romanized_no_space=rom_ns, name_translated=name_trans,
                          artist=art, song_id=song_id, link_nov=link_n, link_adv=link_a, link_exh=link_e, link_max=link_m,
                          diff_nov = dif_n, diff_adv = dif_a, diff_exh = dif_e, diff_max = dif_m, diff_max_type=m_dif,
                          link_jacket=jacket, link_video_play=v_p, link_video_nfx=v_nfx, link_video_og=v_og))


# Recreates the entire db
async def recreate_db():
    # Create a backup
    session = session_maker()
    now = datetime.now()
    old_name = 'sdvxCharts-'+str(now.year)+'-'+str(now.month)+'-'+str(now.day)+'-'+str(now.hour)+'-'+str(now.minute)+'.db'
    if os.path.isfile('sdvxCharts.db'):
        os.rename('sdvxCharts.db', old_name)

    try:
        base.metadata.create_all(engine)
        await init(session, 0)
        session.commit()
        return True

    except Exception as e:
        print(e)
        session.rollback()
        os.remove('sdvxCharts.db')
        if os.path.isfile(old_name):
            os.rename(old_name, 'sdvxCharts.db')
        return False

    finally:
        session.close()


async def update_db(song_id=None):
    session = session_maker()
    try:
        base.metadata.create_all(engine)
        # If URL passed
        link_regex = r'sdvx\.in/(\d+)/(\d+)[naeighm]'
        if re.search(link_regex, str(song_id)) is not None:
            await parse_chart('http://sdvx.in/' + re.search(link_regex, str(song_id)).group(1) + '/js/' + re.search(link_regex, str(song_id)).group(2) + 'sort.js', session, re.search(link_regex, str(song_id)).group(2))
            session.commit()
            return True

        # If a URL was not passed
        await init(session, song_id)
        session.commit()
        return True

    except Exception as e:
        print(e)
        session.rollback()
        return False

    finally:
        session.close()


# I had issues passing these values directly to query search, so I'm using global
song_list, song_result_list = [], []
result_value = 0

async def query(search):
    jp_regex = r'[\u3000-\u303F]|[\u3040-\u309F]|[\u30A0-\u30FF]|[\uFF00-\uFFEF]|[\u4E00-\u9FAF]|[\u2605-\u2606]|[\u2190-\u2195]|\u203B|\u03A9'  # https://gist.github.com/ryanmcgrath/982242
    link_regex = r'sdvx\.in/(\d+)/(\d+)[naeighm]'
    session = session_maker()
    global song_list
    global song_result_list
    global result_value

    # Clear out on new query request
    del song_list[:]
    del song_result_list[:]
    result_value = 0

    for id, name, rom, rom_ns, trans, art, s_id, link_n, link_a, link_e, link_m, \
        v_p, v_nfx, v_og, jk, dif_n, dif_a, dif_e, dif_m, m_dif  in \
            session.query(Chart.id, Chart.name, Chart.name_romanized, Chart.name_romanized_no_space, Chart.name_translated,
                          Chart.artist, Chart.song_id, Chart.link_nov, Chart.link_adv, Chart.link_exh, Chart.link_max,
                          Chart.link_video_play, Chart.link_video_nfx, Chart.link_video_og, Chart.link_jacket,
                          Chart.diff_nov, Chart.diff_adv, Chart.diff_exh, Chart.diff_max, Chart.diff_max_type):
        song_list.append(Song(id, name, rom, rom_ns, trans, art, s_id, link_n, link_a, link_e, link_m, v_p, v_nfx, v_og,
                              jk, dif_n, dif_a, dif_e, dif_m, m_dif))


    # If search is a song url, skip all of the other searches
    # Search to see if it exists
    if re.search(link_regex, search) is not None:
        query_searcher(re.search(link_regex, search).group(2), 4)

        check = False
        for song in song_result_list:
            if song.song_id == re.search(link_regex, search).group(2):
                song_result_list = [song]
                check = True

        if check is False:
            song_result_list = []

        session.close()
        return song_result_list

    # If text contains japanese, it is most likely the title / partial official title
    if re.search(jp_regex, search) is not None:
        query_searcher(search, 0)

        # May the Magical sky building of emotions haunt us no more
        # Substrings in the song name shall come forth superior to fuzzy wuzzy
        temp_list = []
        for song in song_result_list:
            if search in song.name:
                temp_list.append(song)

        song_result_list = temp_list

    # Search song_id for updates
    elif re.search(r'0\d{4}', search) is not None:
        query_searcher(search, 4)

    else:
        # Search through the romanized list
        query_searcher(search, 1)
        # Search through the romanized list with no spaces
        query_searcher(search, 2)
        # Search through the translated list
        query_searcher(search, 3)

        # There were some issues where fuzzy 100 was hit amongst multiple titles, even with exact names.
        # Sadly, Erin couldn't help us.
        # In case the full title was actually given:
        for song in song_result_list:
            if song.name == search:
                song_result_list = [song]

    session.close()

    return song_result_list


def query_searcher(search, type):
    global song_list
    global song_result_list
    global result_value

    for song in song_list:
        song_name = (song.name if type == 0 else
                    song.name_romanized if type == 1 else
                    song.name_rom_no_space if type == 2 else
                    song.name_translated if type == 3 else
                    song.song_id)
        fuzz_value = fuzz.token_set_ratio(song_name, search)

        if fuzz_value > result_value:
            result_value = fuzz_value
            song_result_list = [song]
        elif fuzz_value == result_value and song not in song_result_list:
            song_result_list.append(song)
        # Some cases of difference too big, even though the substring was part of it in jp text
        # Maybe this will find use in the other searches. If so, I'll allow it, maybe.
        elif type == 0 and search in song_name:
            song_result_list.append(song)


async def random_song(level=0):
    session = session_maker()
    song_list = []
    for id, name, rom, rom_ns, trans, art, s_id, link_n, link_a, link_e, link_m, \
        v_p, v_nfx, v_og, jk, dif_n, dif_a, dif_e, dif_m, m_dif  in \
            session.query(Chart.id, Chart.name, Chart.name_romanized, Chart.name_romanized_no_space, Chart.name_translated,
                          Chart.artist, Chart.song_id, Chart.link_nov, Chart.link_adv, Chart.link_exh, Chart.link_max,
                          Chart.link_video_play, Chart.link_video_nfx, Chart.link_video_og, Chart.link_jacket,
                          Chart.diff_nov, Chart.diff_adv, Chart.diff_exh, Chart.diff_max, Chart.diff_max_type):
        song_list.append(Song(id, name, rom, rom_ns, trans, art, s_id, link_n, link_a, link_e, link_m, v_p, v_nfx, v_og,
                              jk, dif_n, dif_a, dif_e, dif_m, m_dif))
    if level < 1:
        return [random.choice(song_list)]

    else:
        level_list = []
        for song in song_list:
            if song.diff_max == level or song.diff_exh == level or song.diff_adv == level or song.diff_nov == level:
                level_list.append(song)

        if len(level_list) > 0:
            return [random.choice(level_list)]
        else:
            return [random.choice(song_list)]