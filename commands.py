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

# Embed colors
#   # General: 0x946b9c
#   # Good: 0x2ecc71
#   # In Progress: 0xe67e22
#   # Warning: 0xf1c40f
#   # Bad: 0xe74c3c

# Messages
async def on_message(message, client):
    global timeoutList
    global sdvxDBUpdate

    commandList = ('!sdvxin', '!cro')

    if message.content.startswith(commandList):

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
                em = discord.Embed(title='Database updating', color=0xf1c40f,
                                   description='Database is currently updating. Please wait.\n'
                                               'Please refer to bot playing status to see when this is done.')
                await client.send_message(message.channel, embed=em)
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

                        em.add_field(name=songList[0].artist, inline=False, value=val)
                    else:
                        em.add_field(name=songList[0].artist, inline=False, value='[NOVICE]('+str(songList[0].linkNov)+') - [ADVANCED]('+str(songList[0].linkAdv)+') - [EXHAUST]('+str(songList[0].linkExh)+')')

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
                    em = discord.Embed(title='Search Error', color=0x946b9c,
                                       description='No Song Found / Error With Query or Database')
                    await client.send_message(message.channel, embed=em)
                elif len(songList) > 20:
                    em = discord.Embed(title='Search Error', color=0xe67e22,
                                       description='Too many songs found. Please refine your search.')
                    await client.send_message(message.channel, embed=em)
                else:
                    # Set up embed
                    em = discord.Embed(title='Multiple songs found.', color=0xe67e22)

                    msg = ''
                    for song in songList:
                        msg += song.name + '\n'

                    em.add_field(name='Please enter the exact title from the list below.', value=msg)
                    await client.send_message(message.channel, embed=em)

            if message.content == '!sdvxin random':
                await sendMessage(await sdvxCharts.randomSong())

            # update command
            elif message.content.startswith('!sdvxin update'):
                # update function to reduce clutter
                async def updateDB(msg, songID = 1):
                    global sdvxDBUpdate

                    sdvxDBUpdate = True
                    await client.change_presence(game=discord.Game(name='Updating SDVX DB'))

                    status = await sdvxCharts.updateDB(songID)

                    sdvxDBUpdate = False

                    # If specific song update, return back for better update message
                    if songID != 1:
                        return

                    await client.change_presence(game=None)
                    if status:
                        em = discord.Embed(title='Success', color=0x2ecc71,
                                           description='Database updated.')
                        await client.edit_message(msg, embed=em)
                    else:
                        em = discord.Embed(title='Failure', color=0xe74c3c,
                                           description='Database update failed.')
                        await client.edit_message(msg, embed=em)

                # Check to see if database is already being updated
                if sdvxDBUpdate:
                    em = discord.Embed(title='Database updating', color=0xf1c40f,
                                       description='Database is already updating.')
                    await client.send_message(message.channel, embed=em)
                    return

                # Check for update override ; Only I can do this
                if message.content == '!sdvxin update override' and message.author.id == str(81415254252191744):
                    em = discord.Embed(title='Updating', color=0x946b9c,
                                       description='Updating SDVX DB...')
                    msg = await client.send_message(message.channel, embed=em)
                    await updateDB(msg)
                    return

                # To update only specific songs
                # Useful for updates to videos/images/etc
                # Updates a single song rather than all of them, which saves a LOT of time
                if re.search(r'!sdvxin\s.+\s(.+)', message.content) is not None:
                    name = re.search(r'!sdvxin\s.+\s(.+)', message.content).group(1)
                    try:
                        songList = await sdvxCharts.query(name)
                        # If song already exists
                        if len(songList) == 1:
                            # Override for me. Too much power.
                            if 'override' in message.content and message.author.id == str(81415254252191744):
                                em = discord.Embed(title='Updating', color=0x946b9c,
                                                   description='Updating ' + songList[0].name + '...')
                                em.set_thumbnail(url=songList[0].jacket)
                                msg = await client.send_message(message.channel, embed=em)
                                await updateDB(msg, songList[0].songID)

                                songList = await sdvxCharts.query(name)
                                em = discord.Embed(title='Database update finished', color=0xe67e22,
                                                   description=songList[0].name + ' updated.')
                                em.set_thumbnail(url=songList[0].jacket)
                                await client.edit_message(msg, embed=em)

                            # Regular user update
                            else:
                                em = discord.Embed(title='Database update vote', color=0xf1c40f,
                                                   description='Database update requested for ' + songList[0].name + '\n'
                                                               'Please react 👍 to vote for an update.\n'
                                                               'Song will be updated if 3 votes are received in the next minute.')
                                em.set_thumbnail(url=songList[0].jacket)
                                msg = await client.send_message(message.channel, embed=em)
                                await client.add_reaction(msg, '👍')
                                await asyncio.sleep(5) # mod 60

                                cached_msg = discord.utils.get(client.messages, id=msg.id)
                                for react in cached_msg.reactions:
                                    if react.emoji == '👍':
                                        if react.count >= 2: # mod 4
                                            em = discord.Embed(title='Database update started', color=0xe67e22,
                                                               description='Enough votes were received.\n'
                                                                           'Now updating ' + songList[0].name + '.\n'
                                                                           'Please refer to the bot\'s game status for status.')
                                            em.set_thumbnail(url=songList[0].jacket)
                                            await client.edit_message(msg, embed=em)
                                            await updateDB(msg, songList[0].songID)

                                            songList = await sdvxCharts.query(name)
                                            em = discord.Embed(title='Database update finished', color=0xe67e22,
                                                              description=songList[0].name + ' updated.')
                                            em.set_thumbnail(url=songList[0].jacket)
                                            await client.edit_message(msg, embed=em)

                                        else:
                                            em = discord.Embed(title='Song update vote failed', color=0xe74c3c,
                                                               description='Not enough votes were received. ' + songList[0].name + ' will not be updated. \n'
                                                                           'Only ' + str(react.count - 1) + ' votes were received. 3 were required.')
                                            await client.edit_message(msg, embed=em)

                        # For completely new songs
                        elif len(songList) == 0:
                            linkRegex = r'sdvx\.in/(\d+)/(\d+)[naeighm]'
                            if re.search(linkRegex, message.content):
                                em = discord.Embed(title='Database update vote', color=0xf1c40f,
                                                   description='Database update requested for '
                                                               '[' + name + '](' + name + ')\n'
                                                               'Please react 👍 to vote for an update.\n'
                                                               'Song will be updated if 3 votes are received in the next minute.')
                                msg = await client.send_message(message.channel, embed=em)
                                await client.add_reaction(msg, '👍')
                                await asyncio.sleep(60)

                                cached_msg = discord.utils.get(client.messages, id=msg.id)
                                for react in cached_msg.reactions:
                                    if react.emoji == '👍':
                                        if react.count >= 4: # modified 4
                                            em = discord.Embed(title='Database update started', color=0xe67e22,
                                                               description='Enough votes were received.\n'
                                                                           'Now updating '
                                                                           '[' + name + '](' + name + ')\n'
                                                                           'Please refer to the bot\'s game status for status.')
                                            await client.edit_message(msg, embed=em)
                                            await updateDB(msg, message.content)

                                            em = discord.Embed(title='Database update finished', color=0xe67e22,
                                                               description='[' + name + '](' + name + ')' + ' updated.')
                                            await client.edit_message(msg, embed=em)

                                        else:
                                            em = discord.Embed(title='Song update vote failed', color=0xe74c3c,
                                                               description='Not enough votes were received. '
                                                                           '[' + name + '](' + name + ') will not be updated. \n'
                                                                           'Only ' + str(react.count - 1) + ' votes were received. 3 were required.')
                                            await client.edit_message(msg, embed=em)

                            else:
                                em = discord.Embed(title='Search Error', color=0x946b9c,
                                                   description='No Song Found / Error With Query or Database')
                                await client.send_message(message.channel, embed=em)

                        elif len(songList) > 20:
                            em = discord.Embed(title='Search Error - Update', color=0xe67e22,
                                               description='Too many songs found. Please refine your search.')
                            await client.send_message(message.channel, embed=em)

                        else:
                            em = discord.Embed(title='Multiple songs found - Update', color=0xe67e22)
                            msg = ''
                            for song in songList:
                                msg += song.name + '\n'

                            em.add_field(name='Please enter the exact title from the list below.', value=msg)
                            await client.send_message(message.channel, embed=em)

                    except Exception as e:
                        print('sdvx error: ' + name + ' ' + str(e))

                else:
                    # General update run
                    em = discord.Embed(title='Database update vote', color=0xf1c40f,
                                       description='sdvx.in database update was requested.\n'
                                                   'Please react 👍 to vote for an update.\n'
                                                   'Database will update if 5 votes are received in the next minute.')
                    msg = await client.send_message(message.channel, embed=em)
                    await client.add_reaction(msg, '👍')
                    await asyncio.sleep(60)

                    cached_msg = discord.utils.get(client.messages, id=msg.id)
                    for react in cached_msg.reactions:
                        if react.emoji == '👍':
                            if react.count >= 6:
                                em = discord.Embed(title='Database update started', color=0xe67e22,
                                                   description='Enough votes were received.\n'
                                                               'Now updating database. Please refer to the bot\'s game status for status.')
                                await client.edit_message(msg, embed=em)
                                await updateDB(msg)

                            else:
                                em = discord.Embed(title='Database update vote failed', color=0xe74c3c,
                                                   description='Not enough votes were received. Database will not be updated. \n'
                                                               'Only ' + str(react.count - 1) + ' votes were received. 5 were required.')
                                await client.edit_message(msg, embed=em)

            # Command to update sdvx.in database structure
            elif message.content == '!sdvxin structureupdate':
                if message.author.id == str(81415254252191744):
                    sdvxDBUpdate = True
                    await client.change_presence(game=discord.Game(name='Updating SDVX DB'))
                    em = discord.Embed(title='Updating', color=0x946b9c,
                                       description='Updating SDVX DB Structure...')
                    msg = await client.send_message(message.channel, embed=em)
                    status = await sdvxCharts.recreateDB()
                    sdvxDBUpdate = False
                    await client.change_presence(game=None)
                    if status:
                        em = discord.Embed(title='Success', color=0x2ecc71,
                                           description='Database structure updated.')
                        await client.edit_message(msg, embed=em)
                    else:
                        em = discord.Embed(title='Failure', color=0xe74c3c,
                                           description='Database structure failed.')
                        await client.edit_message(msg, embed=em)

            else:
                # voltex query
                name = re.search(r'(!sdvxin\s)(.*)', message.content).group(2)
                songList = []
                try:
                    songList = await sdvxCharts.query(name)
                except Exception as e:
                    print('sdvx error: ' + name + ' ' + str(e))

                await sendMessage(songList)

        # For bot specific commands
        elif message.content.startswith('!cro'):
            if message.content == '!cro help':
                em = discord.Embed(title='Commands', color=0x946b9c,
                                   description='!sdvxin title - Searches for title in the cached sdvx.in database\n'
                                               '!sdvxin random - Returns a random song from the sdvx.in database\n'
                                               '!sdvxin update - Updates the sdvx.in database; Doesn\'t overwrite existing songs\n'
                                               '!sdvxin update songTitle/songID/URL - Updates a specific song and overwrites all data for it\n'
                                               '!cro help - Returns this message')
                await client.send_message(message.channel, embed=em)