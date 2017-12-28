import os
import re
import requests
from retrying import retry
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

# Song class for query
class Song():
    def __init__(self, n, nr, nrns, nt, ln, la, le, lm, md):
        self.name = n
        self.nameRomanized = nr
        self.nameRomNoSpace = nrns
        self.nameTranslated = nt
        self.linkNov = ln
        self.linkAdv = la
        self.linkExh = le
        if lm is None:
            self.linkMax = ''
            self.maxDif = 0
        else:
            self.linkMax = lm
            self.maxDif = md

    def all(self):
        return self.name+' '+self.nameRomanized+' '+self.nameRomNoSpace+' '+self.nameTranslated+' '+self.linkNov+' '+self.linkAdv+' '+self.linkExh+' '+self.linkMax

# Database setup

base = declarative_base()
class Chart(base):
    __tablename__ = 'charts'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    nameRomanized = Column(String)
    nameRomNoSpace = Column(String)
    nameTranslated = Column(String)

    linkNov = Column(String)
    linkAdv = Column(String)
    linkExh = Column(String)
    linkMax = Column(String)
    maxDif = Column(Integer)

    def __repr__(self):
        return "<Chart(name: '%s', romanized: '%s', nov: '%s', adv: '%s', exh: '%s', inf: '%s')>" % (
            self.name, self.nameRomanized, self.linkNov, self.linkAdv, self.linkExh, self.linkMax)

engine = create_engine('sqlite:///sdvxCharts.db')
sessionMaker = sessionmaker(bind=engine)

# Initial DB set up
@retry(stop_max_attempt_number=7, wait_fixed=500)
async def init(session):
    print('Starting database entry')

    sortList = ['http://sdvx.in/sort/sort_a.js', 'http://sdvx.in/sort/sort_k.js', 'http://sdvx.in/sort/sort_s.js',
                'http://sdvx.in/sort/sort_t.js', 'http://sdvx.in/sort/sort_n.js', 'http://sdvx.in/sort/sort_h.js',
                'http://sdvx.in/sort/sort_m.js', 'http://sdvx.in/sort/sort_y.js', 'http://sdvx.in/sort/sort_r.js', 'http://sdvx.in/sort/sort_w.js']

    for item in sortList:
        await parseSort(item, session)

@retry(stop_max_attempt_number=7, wait_fixed=500)
async def parseSort(name, session):
    print('Parsing '+ name)

    loop = asyncio.get_event_loop()
    future = loop.run_in_executor(None, requests.get, name)
    futureResult = await future
    req = futureResult.text.split('\n')

    # Sift through the sort js file to get the urls of the charts
    regex = r'/\d.*js'
    for line in req:
        if re.search(regex, line) is not None:
            parse = re.findall(regex, line)[0]
            await parseChart('http://sdvx.in'+parse, session)

@retry(stop_max_attempt_number=7, wait_fixed=500)
async def parseChart(name, session):
    print('Parsing ' + name)

    loop = asyncio.get_event_loop()
    future = loop.run_in_executor(None, requests.get, name)
    futureResult = await future
    req = futureResult.text.split('\n')

    # Sift through the chart js file to get information
    nameRegex = r'(\d+)\s+(.+)' # Group 1 is sdvx.in's id for the song; Group 2 is the song name
    sortRegex = r'SORT\d*' # Used to filter out the sort line
    difRegex = r'LV\d+[NAEIGHM]'
    novRegex = r'LV\d+N'
    advRegex = r'LV\d+A'
    exhRegex = r'LV\d+E'
    maxRegex = r'LV\d+[IGHM]'
    linkRegex = r'/\d.*htm'
    jpRegex = r'[\u3000-\u303F]|[\u3040-\u309F]|[\u30A0-\u30FF]|[\uFF00-\uFFEF]|[\u4E00-\u9FAF]|[\u2605-\u2606]|[\u2190-\u2195]|\u203B' # https://gist.github.com/sym3tri/980083
    name, nameTrans, rom, romPronunciation, linkN, linkA, linkE, linkM = (None,)*8
    mDif = 0
    for i, line in enumerate(req):
        # If the line contains a difficulty link
        if re.search(difRegex, line) is not None and re.search(sortRegex, line) is None:
            # If line has nov difficulty
            if re.search(novRegex, line) is not None:
                linkN = 'http://sdvx.in'+re.search(linkRegex, line).group(0)
            # If line has adv difficulty
            elif re.search(advRegex, line) is not None:
                linkA = 'http://sdvx.in'+re.search(linkRegex, line).group(0)
            # If line has exh difficulty
            elif re.search(exhRegex, line) is not None:
                linkE = 'http://sdvx.in'+re.search(linkRegex, line).group(0)
            # If line has max difficulty
            elif re.search(maxRegex, line) is not None:
                linkM = 'http://sdvx.in'+re.search(linkRegex, line).group(0)
                # Set difficulty value
                if 'I' in line:
                    mDif = 1
                elif 'G' in line:
                    mDif = 2
                elif 'H' in line:
                    mDif = 3
                elif 'M' in line:
                    mDif = 4

        # If first line
        elif i == 0:
            # Get name of the song
            name = html.unescape(re.search(nameRegex, line).group(2))

            # Get romanized jp title

            # Only toss to google if it contains jp
            if re.search(jpRegex, name) is not None:
                futureNT = loop.run_in_executor(None, lambda: Translator().translate(name, src='ja', dest='en'))
                futureP = loop.run_in_executor(None, lambda: Translator().translate(name, dest='ja'))
                futureNTResult = await futureNT
                futurePResult = await futureP
                nameTrans = futureNTResult.text
                romPronunciation = futurePResult.pronunciation
            # If received jp from google, save as rom - decoded without pronunciation guides
            if romPronunciation is not None:
                rom = unidecode(romPronunciation)
            # If nothing received from google, assume no jp and save title as rom
            else:
                nameTrans = name
                rom = name

    romNS = rom.replace(' ', '')

    await addToDB(name, nameTrans, rom, romNS, linkN, linkA, linkE, linkM, mDif, session)

async def addToDB(name, nameTrans, rom, romNS, linkN, linkA, linkE, linkM, mDif, session):
    #print('Adding ' + name +' '+ rom +' '+ linkN +' '+ linkA +' '+ linkE +' '+ linkM)
    session.add(Chart(name=name, nameRomanized=rom, nameRomNoSpace=romNS, nameTranslated=nameTrans, linkNov=linkN, linkAdv=linkA, linkExh=linkE, linkMax=linkM, maxDif=mDif))

# Used for updates until a proper update function is created
async def recreateDB():
    # Create a backup
    session = sessionMaker()
    now = datetime.now()
    oldName = 'sdvxCharts-'+str(now.year)+'-'+str(now.month)+'-'+str(now.day)+'-'+str(now.hour)+'-'+str(now.minute)+'.db'
    if os.path.isfile('sdvxCharts.db'):
        os.rename('sdvxCharts.db', oldName)
    try:
        base.metadata.create_all(engine)
        await init(session)
        session.commit()
        return True
    except Exception as e:
        print(e)
        session.rollback()
        session.close()
        os.remove('sdvxCharts.db')
        os.rename(oldName, 'sdvxCharts.db')
        return False
    finally:
        session.close()

# I had issues passing these values directly to query search, so I'm using global
songList, songResultList = [], []
resultValue = 0

async def query(search):
    jpRegex = r'[\u3000-\u303F]|[\u3040-\u309F]|[\u30A0-\u30FF]|[\uFF00-\uFFEF]|[\u4E00-\u9FAF]|[\u2605-\u2606]|[\u2190-\u2195]|\u203B'  # https://gist.github.com/ryanmcgrath/982242
    session = sessionMaker()
    global songList
    global songResultList
    global resultValue

    # Clear out on new query request
    del songList[:]
    del songResultList[:]
    resultValue = 0

    for name, rom, romNS, trans, linkN, linkA, linkE, linkM, mDif in session.query(Chart.name, Chart.nameRomanized, Chart.nameRomNoSpace, Chart.nameTranslated,
                                                                                   Chart.linkNov, Chart.linkAdv, Chart.linkExh, Chart.linkMax, Chart.maxDif):
        songList.append(Song(name, rom, romNS, trans, linkN, linkA, linkE, linkM, mDif))

    # If text contains japanese, it is most likely the title / partial official title
    if re.search(jpRegex, search) is not None:
        querySearcher(search, 0)

    else:
        # Search through the romanized list
        querySearcher(search, 1)
        # Search through the romanized list with no spaces
        querySearcher(search, 2)
        # Search through the translated list
        querySearcher(search, 3)

    session.close()

    return songResultList

def querySearcher(search, type):
    global songList
    global songResultList
    global resultValue

    for song in songList:
        fuzzValue = fuzz.token_set_ratio(song.name if type == 0 else
                                         song.nameRomanized if type == 1 else
                                         song.nameRomNoSpace if type == 2 else
                                         song.nameTranslated, search)
        if fuzzValue > resultValue:
            resultValue = fuzzValue
            songResultList = [song]
        elif fuzzValue == resultValue and song not in songResultList:
            songResultList.append(song)
