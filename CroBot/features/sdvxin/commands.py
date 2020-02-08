#
# commands.py
# Parses !sdvxin commands and does work based on the command
# # Only discord related work should be done, such as sending/editing/reacting messages
# # sdvx.in related work should be sent to sdvx.py
#

# External imports
import re
import configparser
import discord

# Internal imports
from command import Command
from CroBot.features.sdvxin import sdvx, embeds, regex

# To keep track of db updates
sdvx_db_update = False


# Command tracker
sdvx_command = Command('!sdvxin')


######################
# DATABASE FUNCTIONS #
######################


async def ongoing_update(message):
    """
    ongoing_update: Sends a message saying an update is ongoing, if there is one
    :param message: The message to respond to
    :return: True if the update is ongoing
             False if the update is not ongoing
    """
    global sdvx_db_update
    if sdvx_db_update:
        await message.channel.send(embed=embeds.db_update_ongoing())
        return True

    return False


async def error_check(errors, message, song=None):
    """
    error_check: A function to check if the number of errors and send the correct embed accordingly
    :param errors: A list of errors
    :param message: The discord message to edit
    :return: N/A
    """
    # If there are no issues with the update,
    if len(errors) == 0:
        # If there's a song attached
        if song is not None:
            await message.edit(embed=embeds.db_update_song_success(song=song))

        # If there is not a song attached
        else:
            await message.edit(embed=embeds.db_update_success())

    # If there are issues with the update
    else:
        await message.edit(embed=embeds.db_update_failed(errors))


async def update_song(song, message):
    """
    update_song: A helper function to cut down on repetitive code for updating a song since it occurs three times
    :param song: The song to be updated
    :param message: The message to respond to
    :return: N/A
    """
    global sdvx_db_update
    message_update = await message.channel.send(embed=embeds.db_update_song_start(song=song))

    # Attempt to update
    sdvx_db_update = True
    errors = await sdvx.update_song(song.song_id)
    sdvx_db_update = False

    await error_check(errors, message_update, song)


@sdvx_command.register('update')
async def update(client, message):
    """
    update: For the request to update the database
    :param client: Client to update game status
    :param message: The message to reply to
    :return: N/A
    """
    global sdvx_db_update

    # If there already is an update going on
    if await ongoing_update(message):
        return

    await client.change_presence(activity=discord.Game(name='Updating SDVX DB'))

    # If the message is requesting a light update (nothing after update)
    if message.content == '!sdvxin update':
        # Send the update message, start updating the database, and then edit the message to be be the completed embed
        message_update = await message.channel.send(embed=embeds.db_update_start())

        sdvx_db_update = True
        errors = await sdvx.update()
        sdvx_db_update = False

        await error_check(errors, message_update)

    # Otherwise, find the song the user is trying to manually update
    else:
        # If the passed value is a url
        if re.search(regex.link, message.content) is not None:
            # Search for the song given the url
            link = re.search(regex.link, message.content).group(0)
            song = await sdvx.search_song_link(link)

            # If the song exists, update it
            if song is not None:
                await update_song(song, message)

            # If the song does not exist, add it
            else:
                message_update = await message.channel.send(embed=embeds.db_update_song_start(name=link))

                # Attempt to update
                sdvx_db_update = True
                song_id = re.search(regex.song_id, message.content).group(0)
                errors = await sdvx.add_song(song_id)
                sdvx_db_update = False

                song = await sdvx.search_song_id(song_id)
                await error_check(errors, message_update, song)

        # If the passed value is a song_id
        elif re.search(regex.song_id, message.content) is not None:
            # Attempt to update the song based on song_id
            song_id = re.search(regex.song_id, message.content).group(0)
            song = await sdvx.search_song_id(song_id)

            # Send the proper embeds
            # If the song exists
            if song is not None:
                await update_song(song, message)

            # If it does not exist, return a song not found
            # Would prefer not to do song adds by id by user in the case the song is just all numbers (444 gets close)
            else:
                await message.channel.send(embed=embeds.search_not_found())

        # Otherwise, treat it as a general update query
        else:
            query = re.search(regex.update, message.content).group(2)
            song_list = await sdvx.search_song(query)

            # If there has only one song that has been found then go ahead and update it
            if len(song_list) == 1:
                song = song_list[0]
                await update_song(song, message)

            # If there are less than 10, send an embed listing them off
            elif len(song_list) < 10:
                await message.channel.send(embed=embeds.search_list(song_list))

            # Otherwise, there are too many found, send an embed saying too many were found
            else:
                await message.channel.send(embed=embeds.search_too_many())

    await client.change_presence(activity=None)


######################
#  QUERY  FUNCTIONS  #
######################


@sdvx_command.register('random')
async def random(client, message):
    """
    random: The random query for sdvx, obtains a random song and sends it as an embed
    :param client: Not used, sent by default from commands
    :param message: The message to reply to
    :return: N/A
    """
    # If the message just wants a random song
    if message.content == '!sdvxin random':
        song = await sdvx.fetch_random()
        # If there's a song
        if song is not None:
            await message.channel.send(embed=embeds.song(song))

        else:
            await message.channel.send(embed=embeds.search_not_found())

    # Otherwise, if it is a certain level the user wants
    else:
        level = re.search(regex.random, message.content)
        # If a level even exists in this query
        if level is not None:
            level = level.group(1)
            song = await sdvx.fetch_random(level)
            # If there's a song
            if song is not None:
                await message.channel.send(embed=embeds.song(song))

            else:
                await message.channel.send(embed=embeds.search_not_found())

        # If not, kick it over to default, in the case that it's a default song
        else:
            await search(message)


@sdvx_command.register('')
async def default(client, message):
    """
    default: The default query for sdvx.in, it should have a search query behind it
                - Due to how command configuration is done, this should be the last to be instantiated
    :param client: Not used, sent by default from commands
    :param message: The message to reply to
    :return: N/A
    """
    await search(message)


async def search(message):
    """
    search: Helper function for default, so that it can be used with random as a fallback
            Otherwise, it would kick saying the function is NoneType
    :param message: The message to reply to
    :return: N/A
    """
    # Fetch the query and attempt to search for it
    query = re.search(regex.query, message.content).group(2)

    if query is not None:
        # If a song_id was passed, fetch the song and send the embed if it exists.
        # If it doesn't exist, continue down to main query
        if re.search(regex.song_id, message.content) is not None:
            song_id = re.search(regex.song_id, message.content).group(0)
            song = await sdvx.search_song_id(song_id)

            if song is not None:
                await message.channel.send(embed=embeds.song(song))
                return

        # If a link was passed, fetch the song and send the embed if it exists.
        # If it doesn't exist, continue down to main query
        elif re.search(regex.link, message.content) is not None:
            link = re.search(regex.link, message.content).group(0)
            song = await sdvx.search_song_link(link)

            if song is not None:
                await message.channel.send(embed=embeds.song(song))
                return

        # Main query searching
        # Fetch a song_list based on the query
        song_list = await sdvx.search_song(query)

        # If there's only one song, just simply return the only existing song
        if len(song_list) == 1:
            await message.channel.send(embed=embeds.song(song_list[0]))

        # If no songs were found, send the not found embed
        elif len(song_list) == 0:
            await message.channel.send(embed=embeds.search_not_found())

        # If less than 10 errors were found, send a list of songs found
        elif len(song_list) < 10:
            await message.channel.send(embed=embeds.search_list(song_list))

        # Otherwise, too many songs were found, send the too many songs found
        else:
            await message.channel.send(embed=embeds.search_too_many())
