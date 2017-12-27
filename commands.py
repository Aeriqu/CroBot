import discord

import sdvxCharts

import re
import time
from collections import defaultdict

# Timeout setup
INTERVAL = 5
# format: name, time able to talk
timeoutDict = defaultdict(float)

# Messages
async def on_message(message, client):
    global timeoutList
    # sdvx.in functionality
    if message.content.startswith('!sdvxin'):
        # timeout check
        now = time.time()
        # remove all users who have completed timeout
        for user, timeAvailable in list(timeoutDict.items()):
            if timeAvailable <= now:
                del timeoutDict[user]
        # if user still exists, their timeout hasn't finished
        if message.author.id in timeoutDict:
            return
        # add user to list and start query
        timeoutDict[message.author.id] = now + INTERVAL

        # voltex query
        name = re.search(r'(!sdvxin\s)(.*)', message.content).group(2)
        songList = []
        try:
            songList = sdvxCharts.query(name)
        except Exception as e:
            print('sdvx error: '+name+' '+e)

        if len(songList) == 1:
            # Set up embed
            em = discord.Embed(title=songList[0].name, color=0x946b9c)
            if songList[0].maxDif is not 0:
                val = '[NOVICE]('+str(songList[0].linkNov)+') - [ADVANCED]('+str(songList[0].linkAdv)+') - [EXHAUST]('+str(songList[0].linkExh)+') - '

                if songList[0].maxDif is 1:
                    val += '[INFINITE]('+str(songList[0].linkMax)+')'
                elif songList[0].maxDif is 2:
                    val += '[GRAVITY](' + str(songList[0].linkMax) + ')'
                elif songList[0].maxDif is 3:
                    val += '[HEAVENLY](' + str(songList[0].linkMax) + ')'
                elif songList[0].maxDif is 4:
                    val += '[MAXIMUM](' + str(songList[0].linkMax) + ')'

                em.add_field(name='-', value=val)
            else:
                em.add_field(name='-', value='[NOVICE]('+str(songList[0].linkNov)+') - [ADVANCED]('+str(songList[0].linkAdv)+') - [EXHAUST]('+str(songList[0].linkExh)+')')

            await client.send_message(message.channel, embed=em)
        elif len(songList) is 0:
            await client.send_message(message.channel, 'No Song Found / Error With Query or Database')
        else:
            await client.send_message(message.channel, 'Multiple songs found with that request. I\'ll add this later')
