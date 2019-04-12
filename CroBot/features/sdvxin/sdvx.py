#
# sdvx.py
# Main file to call for requests to do various sdvx.in tasks
#


# External imports
import re


# Internal Imports
from CroBot.features.sdvxin import regex
from CroBot.features.sdvxin import request
from CroBot.features.sdvxin import database


####################
# SEARCH FUNCTIONS #
####################

async def search_song(query):
    """
    search_song: Fetches the closest matching song from the database
                    - If multiple are found, return a list of potential songs
    :param query:
    :return:
    """
    # Check to see a link is in the query
    if re.search(regex.link_regex, query) is not None:
        return await search_link(query)

    # Fetch the list of all songs in the database
    # TODO: Only run if a query needs to be made
    song_list = database.song_list()


    return


### Helper Functions for search_song() ###


async def search_link(query):
    """
    search_link: A helper function for search_song() to search for a song
    :param query: The link to parse
    :return: A song dictionary if a song was found
             False if a song was found
             NOTE: Since we are given a link, it should only return one song or none at all
    """
    # Parse the ID of the song
    song_id = re.search(regex.link_regex, query).group(1)

    # Check the database to see if the song exists
    # if database.exist_song(song_id):


    return


####################
# UPDATE FUNCTIONS #
####################


async def update():
    """
    update: Updates the database, adding entries that did not previously exist
    :return: A list of errors
    """
    # TODO: Error catching for songs that failed to be added
    #
    # Fetches the database song list, the online song list, and then gets the difference from them
        # This obtains the list we will need to update
    database_song_list = await database.song_ids()
    online_song_list = await request.song_ids()
    dif_list = list(set(online_song_list['song_ids']) - set(database_song_list))

    # A list of errors to keep track of
    errors = []
    # A database session in order to add songs
    session = await database.session_start()

    # Iterate through the list of songs
    for song_id in dif_list:
        print(song_id)
        # Attempt to fetch the song
        song_dict = await request.song(song_id)

        # If there is an error in the dictionary
        if 'errors' in song_dict:
            # Append the error to the list of errors and then continue, "skipping" this song
            errors.append(song_dict['errors'])
            continue

        # Attempt to add to the database
            # If failed, add to errors
        if await database.add_song(session, song_dict) == False:
            errors.append('Error (Add Update Song Data): ' + song_id)

    # Commit the changes and close the session
    session.commit()
    await database.session_end(session)

    # Return the errors
    # TODO: Use this to count how many errors they are
        # If less than 10, list the ids
        # If more than 10, show how many errors there were
    return errors


async def update_song(song_id):
    """
    update_song: Fetches data to update a song and then updates it
    :param song_id: The id of the song to update
    :return: A list of any errors that may have occured
    """
    # A list of errors to keep track of
    errors = []

    # Attempt to get the dictionary list of songs
    song_dict = await request.song(song_id)

    # If there is an error in the dictionary
    if 'errors' in song_dict:
        # Append the error to the list of errors and then return, preventing the song from being added
        errors.append(song_dict['errors'])
        return errors

    # Create a session
    session = await database.session_start()

    # If the song exists, attempt to update it
    if await database.exist_song(song_id):
        if await database.update_song(session, song_dict) == False:
            errors.append('Error (Database Update Song): ' + song_id)

    else:
        print(song_dict)
        if await database.add_song(session, song_dict) == False:
            errors.append('Error (Database Add Song): ' + song_id)

    session.commit()
    await database.session_end(session)

    return errors

# Note: This implementation is closer to an update request
# async def search_link(link):
#     """
#     search_link: A helper function for search_song() to search for a song
#     :param link:
#     :return:
#     """
#     # Parse the ID of the song
#     song_id = re.search(regex.link_regex, link).group(1)
#
#     # Check to see if the song is already in the database
#     if await database.exist_song(song_id):
#         # TODO: Update the song
#         print()
#
#     else:
#         # Fetch the song
#         song_dict = await request.song(song_id)
#         # Add the song to the database
#         session = await database.session_start()
#         return await database.song_add(session, song_dict)


####################
#  [InsertNameFunctions]  #
####################



