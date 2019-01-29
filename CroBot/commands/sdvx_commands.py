#
# sdvx_commands.py
# Contains all the functions needed for the sdvx.in functionality
#

import discord
import re
import asyncio

from CroBot import sdvx_charts
from CroBot.embeds import sdvx_embeds as embeds

# To keep track of db updates
sdvx_db_update = False

# Owner ID, aka Aeriq. Used for update overrides.
OWNER_ID = '81415254252191744'

# Common Regex
QUERY_REGEX = r'(!sdvxin\s)(.*)'
UPDATE_REGEX = r'(!sdvxin\supdate\s)(.*)'
LINK_REGEX = r'sdvx\.in/(\d+)/(\d+)[naeighm]'

# Vote Settings
VOTE_TIMER = 60

async def request(client, message):
    """
    Handles the request from requests.py
    Main purpose is to redirect to the proper functions
    """
    # Checks to see if there is currently an update running
    if await check_update(client, message):
        # Sends the embed stating that the update is currently ongoing within check_update()
        return

    # If there isn't an update, proceed with directing the requests

    # If message specifies random
    if message.content.startswith('!sdvxin random'):
        await random_chart(client, message)

    # If message specifies an update
    elif message.content.startswith('!sdvxin update'):
        await update_charts(client, message)

    # If it is a regular query
    else:
        await sdvx_query(client, message)


async def check_update(client, message):
    """
    Checks if the client is currently updating
    If it is updating, it sends a message and returns true
    Otherwise, it returns false
    """
    # Check to see if database is currently updating
    if sdvx_db_update:
        await client.send_message(message.channel, embed=embeds.db_update_ongoing())
        return True

    # If the db is not updating
    return False


async def update_db(client, message, song_id=None):
    """
    Used to start the update for sdvx.in
    """
    global sdvx_db_update

    # Starts the update
    sdvx_db_update = True
    await client.change_presence(game=discord.Game(name='Updating SDVX DB'))

    status = await sdvx_charts.update_db(song_id)

    # Update finish
    sdvx_db_update = False
    await client.change_presence(game=None)

    # If there was a link, refresh song_id for a proper embed
    if re.search(LINK_REGEX, str(message.content)) is not None:
        song_id = re.search(LINK_REGEX, str(song_id)).group(2)

    # If a specific song was updated
    if song_id is not None:
        song_list = await sdvx_charts.query(song_id)
        await client.edit_message(message, embed=embeds.db_update_song_success(song_list[0]))
        return

    # If update was successful
    if status:
        await client.edit_message(message, embed=embeds.db_update_success())

    # If update failed
    else:
        await client.edit_message(message, embed=embeds.db_update_failed())


async def send_message(client, message, song_list):
    """
    Used to send a message
    The workflow is based on length of passed songList
    Length: 1 - Sends a song embed
            0 - Sends no song found embed
            >20 - Sends too many found embed
            2-19 - Sends a list of the songs found
    """
    if len(song_list) == 1:
        # Send song embed
        await client.send_message(message.channel, embed=embeds.song(song_list))

    # If no songs were found
    elif len(song_list) == 0:
        await client.send_message(message.channel, embed=embeds.search_not_found())

    # If too many songs were found
    elif len(song_list) > 20:
        await client.send_message(message.channel, embed=embeds.search_too_many())

    # Sends a list of the songs
    else:
        await client.send_message(message.channel, embed=embeds.search_list(song_list))


async def sdvx_query(client, message):
    """
    Completes a general sdvx.in query.
    Message comes in as !sdvxin [song_identifier]
    """
    name = re.search(QUERY_REGEX, message.content).group(2)
    songList = []
    try:
        songList = await sdvx_charts.query(name)
    except Exception as e:
        print('sdvx error: ' + name + ' ' + str(e))

    await send_message(client, message, songList)


async def random_chart(client, message):
    """
    Used to grab a random chart from the sdvx.in db
    Level is specified in case the user wants to random a difficulty level
    """
    # If the request is exactly !sdvxin random, give the user a completely random chart
    if message.content == ('!sdvxin random'):
        await send_message(client, message, await sdvx_charts.random_song())

    elif message.content.startswith('!sdvxin random'):
        # If a random number is specified
        if re.search(r'!sdvxin random \d+', message.content) is not None:
            await send_message(client, message, await sdvx_charts.random_song(int(re.search(r'\d+', message.content).group(0))))

        # Else, it might be a valid request;
        else:
            sdvx_query(client, message)


async def update_charts(client, message):
    """
    Used to clarify which charts needs to be updated before sending it to update_db
    """

    # If the owner specifies override, moved to reduce clutter
    if message.author.id == OWNER_ID and 'override' in message.content:
        await owner_update(client, message)
        return

    # If not the owner of the bot / override not specified

    # If only a general update is requested
    if message.content == '!sdvxin update':
        msg = await client.send_message(message.channel, embed=embeds.db_update_vote_start())
        await client.add_reaction(msg, '👍')
        # todo: voting
        await asyncio.sleep(VOTE_TIMER)

        cached_msg = discord.utils.get(client.messages, id=msg.id)
        for react in cached_msg.reactions:
            if react.emoji == '👍':
                if react.count >= 5:
                    await client.edit_message(msg, embed=embeds.db_update_vote_success())
                    await update_db(client, msg)
                else:
                    await client.edit_message(msg, embed=embeds.db_update_vote_failed(react=react))

    # If a specific update was requested
    else:
        # todo: on update voting, change async timeout to a on_react system
        # - Have a list with all of the messages that need to be checked with a creation timestamp

        # Grab a song_list from the message; however, it is useless for complete update, which is almost never done
        name = re.search(UPDATE_REGEX, message.content).group(2)
        song_list = await sdvx_charts.query(name)

        try:
            # If the song already exists
            if len(song_list) == 1:
                msg = await client.send_message(message.channel, embed=embeds.db_update_song_vote_start(song=song_list[0]))
                await client.add_reaction(msg, '👍')
                # todo: voting
                await asyncio.sleep(VOTE_TIMER)

                cached_msg = discord.utils.get(client.messages, id=msg.id)
                for react in cached_msg.reactions:
                    if react.emoji == '👍':
                        if react.count >= 3:
                            await client.edit_message(msg, embed=embeds.db_update_song_vote_success(song=song_list[0]))
                            await update_db(client, msg, song_list[0].song_id)
                        else:
                            await client.edit_message(msg, embed=embeds.db_update_song_vote_failed(song=song_list[0], react=react))

            # If the song does not exist
            elif len(song_list) == 0:
                # If there is a link placed
                if re.search(LINK_REGEX, message.content):
                    msg = await client.send_message(message.channel, embed=embeds.db_update_song_vote_start(name=name))
                    await client.add_reaction(msg, '👍')
                    # todo: voting
                    await asyncio.sleep(VOTE_TIMER)

                    cached_msg = discord.utils.get(client.messages, id=msg.id)
                    for react in cached_msg.reactions:
                        if react.emoji == '👍':
                            if react.count >= 3:
                                await client.edit_message(msg, embed=embeds.db_update_song_vote_success(name=name))
                                await update_db(client, msg, name)
                            else:
                                await client.edit_message(msg, embed=embeds.db_update_song_vote_failed(name=name, react=react))
                # If there isn't a link
                else:
                    await client.send_message(message.channel, embed=embeds.search_not_found())

            # If there are too many songs
            elif len(song_list) > 20:
                await client.send_message(message.channel, embed=embeds.search_too_many())

            # List the songs
            else:
                await client.send_message(message.channel, embed=embeds.search_list(song_list))

        except Exception as e:
            # todo: add error exception embed messages
            print(e)


async def owner_update(client, message):
    """
    Owner overrides for updates and stuff
    """

    # If structure update was specified, which completely recreates the db
    if message.content == '!sdvxin update structure override':
        # Start the db recreation
        global sdvx_db_update
        sdvx_db_update = True

        await client.change_presence(game=discord.Game(name='Updating SDVX DB'))

        msg = await client.send_message(message.channel, embed=embeds.db_update_start())

        status = await sdvx_charts.recreate_db()

        # End of db recreation
        sdvx_db_update = False
        await client.change_presence(game=None)

        # If the db recreation was successful
        if status:
            await client.edit_message(msg, embed=embeds.db_update_success())

        # If db recreation failed
        else:
            await client.edit_message(msg, embed=embeds.db_update_failed())

        return

    # If only update is specified, which implies update all
    if message.content == '!sdvxin update override':
        msg = await client.send_message(message.channel, embed=embeds.db_update_start())
        await update_db(client, msg)
        return

    try:
        # If none of the above work, it is just an individual chart update

        # Grab a song_list from the message; however, it is useless for complete update, which is almost never done
        name = re.search(UPDATE_REGEX + '\soverride', message.content).group(2)
        song_list = await sdvx_charts.query(name)

        # If the song_list has 1
        if len(song_list) == 1:
            msg = await client.send_message(message.channel, embed=embeds.db_update_song_start(song_list[0]))
            await update_db(client, msg, song_list[0].song_id)

        # If the song list has 0
        elif len(song_list) == 0:
            if re.search(LINK_REGEX, message.content):
                msg = await client.send_message(message.channel, embed=embeds.db_update_song_start(name=name))
                await update_db(client, msg, message.content)

            else:
                await client.send_message(message.channel, embed=embeds.search_not_found())

        # If there are too many songs
        elif len(song_list) > 20:
            await client.send_message(message.channel, embed=embeds.search_too_many())

        # List the songs
        else:
            await client.send_message(message.channel, embed=embeds.search_list(song_list))

    except Exception as e:
        # todo: add error exception embed messages
        print(e)