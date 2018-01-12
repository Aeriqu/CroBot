import discord

import sdvxCharts

import re
import time
import asyncio

from collections import defaultdict

# Timeout setup
INTERVAL = 5
# format: name, time able to talk
timeoutDict = defaultdict(float)
# To keep track of db updates
sdvxDBUpdate = False

# Messages
async def on_message(message, client):
    global timeoutList
    global sdvxDBUpdate

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

    # sdvx.in functionality
    if message.content.startswith('!sdvxin'):

        # Check to see if database is currently updating
        if sdvxDBUpdate:
            await client.send_message(message.channel, 'Database is currently updating. Please wait.\n'
                                                       'Please refer to bot playing status to see when this is done.')
            return

        async def sendMessage(songList):
            if len(songList) == 1:
                # Set up embed
                em = discord.Embed(title=songList[0].name, color=0x946b9c)
                em.set_thumbnail(url=songList[0].jacket)
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

                    em.add_field(name=songList[0].artist, value=val)
                else:
                    em.add_field(name=songList[0].artist, value='[NOVICE]('+str(songList[0].linkNov)+') - [ADVANCED]('+str(songList[0].linkAdv)+') - [EXHAUST]('+str(songList[0].linkExh)+')')

                # Video field
                if songList[0].videoPlay is not '' or songList[0].videoNFX is not '' or songList[0].videoOG is not '':
                    val = ''
                    nam = 'Video'
                    # In game video
                    if songList[0].videoPlay is not '':
                        val += '[PLAY]('+songList[0].videoPlay+')'
                    # Separator pt 1
                    if songList[0].videoPlay is not '' and songList[0].videoNFX is not '':
                        val += ' - '
                        nam = 'Videos'
                    # NOFX video
                    if songList[0].videoNFX is not '':
                        val += '[NO FX]('+songList[0].videoNFX+')'
                    # Separator pt 2 - I should find a better way to do this
                    if songList[0].videoNFX is not '' and songList[0].videoOG is not '':
                        val += ' - '
                        nam = 'Videos'
                    # Sometimes has an other
                    if songList[0].videoOG is not '':
                        val += '[OTHER](' + songList[0].videoOG + ')'
                    em.add_field(name=nam, value=val)

                # Send Embed
                await client.send_message(message.channel, embed=em)
            elif len(songList) == 0:
                await client.send_message(message.channel, 'No Song Found / Error With Query or Database')
            elif len(songList) > 10:
                await client.send_message(message.channel, 'Too many songs found. Please refine your search.')
            else:
                # Set up embed
                em = discord.Embed(title='Multiple songs found.', color=0x946b9c)

                msg = ''
                for song in songList:
                    msg += song.name + '\n'

                em.add_field(name='Please enter the exact title from the list below.', value=msg)
                await client.send_message(message.channel, embed=em)

        if message.content == '!sdvxin random':
            await sendMessage(await sdvxCharts.randomSong())

        else:
            # voltex query
            name = re.search(r'(!sdvxin\s)(.*)', message.content).group(2)
            songList = []
            try:
                songList = await sdvxCharts.query(name)
            except Exception as e:
                print('sdvx error: '+name+' '+e)

            await sendMessage(songList)



    # Command to update sdvx.in database
    elif message.content.startswith('!sdvxupdate'):

        # update function to reduce clutter
        async def updateDB(msg):
            global sdvxDBUpdate

            sdvxDBUpdate = True
            await client.change_presence(game=discord.Game(name='Updating SDVX DB'))

            status = await sdvxCharts.updateDB()

            sdvxDBUpdate = False
            await client.change_presence(game=None)
            if status:
                await client.edit_message(msg, new_content='Database updated.')
            else:
                await client.edit_message(msg, new_content='Database update failed.')

        # Check to see if database is already being updated
        if sdvxDBUpdate:
            await client.send_message(message.channel, 'Database is already updating.')
            return

        # If not bot owner, aka me
        if message.author.id != str(81415254252191744):
            msg = await client.send_message(message.channel, 'sdvx.in database update was requested.\n'
                                                             'Please react 👍 to vote for an update.\n'
                                                             'Database will update if 5 votes are received in the next minute.')
            await client.add_reaction(msg, '👍')
            await asyncio.sleep(60)

            cached_msg = discord.utils.get(client.messages, id=msg.id)
            for react in cached_msg.reactions:
                if react.emoji == '👍':
                    if react.count >= 6:
                        await client.edit_message(msg, new_content='Enough votes were received.\n'
                                                                   'Now updating database. Please refer to the bot\'s game status for status.')
                        await updateDB(msg)

                    else:
                        await client.edit_message(msg, new_content='Not enough votes were received. Database will not be updated. \n'
                                                                   'Only '+str(react.count-1)+' votes were received. 5 were required.')
        # If bot owner, aka me
        else:
            msg = await client.send_message(message.channel, 'Updating SDVX DB...')
            await updateDB(msg)

    # Command to update sdvx.in database structure
    elif message.content.startswith('!sdvxstructureupdate'):
        if message.author.id == str(81415254252191744):
            sdvxDBUpdate = True
            await client.change_presence(game=discord.Game(name='Updating SDVX DB'))
            msg = await client.send_message(message.channel, 'Updating SDVX DB Structure...')
            status = await sdvxCharts.recreateDB()
            sdvxDBUpdate = False
            await client.change_presence(game=None)
            if status:
                await client.edit_message(msg, new_content='Database structure updated.')
            else:
                await client.edit_message(msg, new_content='Database structure update failed.')

    # For bot specific commands
    elif message.content.startswith('!cro'):
        if message.content == '!cro help':
            em = discord.Embed(title='-', color=0x946b9c)
            em.add_field(name='-', value='!sdvxin [title] - Searches for title in the cached sdvx.in database\n'
                                         '!sdvxin random - Returns a random song from the sdvx.in database\n'
                                         '!sdvxupdate - Updates the sdvx.in database\n'
                                         '!cro help - Returns this message')
            await client.send_message(message.channel, embed=em)