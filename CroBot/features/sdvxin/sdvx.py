#
# sdvx.py
# Main file to call for requests to do various sdvx.in tasks
#


# External imports
import re
import random
from fuzzywuzzy import fuzz


# Internal Imports
from CroBot.features.sdvxin import regex
from CroBot.features.sdvxin import request
from CroBot.features.sdvxin import database


####################
# SEARCH FUNCTIONS #
####################


async def compare_fuzz(song, best_matches, best_fuzz_ratio, fuzz_value):
    """
    compare_fuzz: A helper function to compare fuzz values then add it to the best_matches array, if needed
    :param song: The song to potentially add
    :param best_matches: A list of best matches
    :param best_fuzz_ratio: The currently best fuzz ratio
    :param fuzz_value:
    :return: True if the fuzz_ratio was better and needs to be updated
             False if the fuzz_ratio does not need to be modified
    """
    # If fuzz_value is greater than best_fuzz ratio, set best to fuzz_value and set best_matches to only that song
    if fuzz_value > best_fuzz_ratio:
        best_matches.clear()
        best_matches.append(song)
        return True

    # Otherwise, if fuzz and best are equal, add the song to the list
    elif fuzz_value == best_fuzz_ratio:
        best_matches.append(song)
        return False

    return False


async def search_song(query):
    """
    search_song: Fetches the closest matching song from the database
                    - If multiple are found, return a list of potential songs
    :param query: A query in string format, usually the name of a song
    :return: A list of best matches for the given query
    """
    # Fetch the list of all songs in the database
    song_list = await database.song_list()

    # Checks for song list iteration
    is_japanese = re.search(regex.japanese, query) is not None

    # Keep track of "best" matches and ratios
    best_fuzz_ratio = 0
    best_matches = []

    # Loop through the song lists and attempt to find something that matches the query
    for song in song_list:
        # If there's japanese in the user provided phrase, generally implying that it is typed properly/copy pasted
            # Only look at the japanese field for fuzz comparisons
        if is_japanese:
            fuzz_value = fuzz.token_set_ratio(song.title, query)
            if await compare_fuzz(song, best_matches, best_fuzz_ratio, fuzz_value):
                best_fuzz_ratio = fuzz_value


        # Otherwise, go through all of the romanized texts (translated and romanized to find a better match)
        else:
            # Obtain lowercased comparisons of both translated and romanized texts
            fuzz_value_translated = fuzz.token_set_ratio(song.title_translated.lower(), query.lower())
            fuzz_value_romanized = fuzz.token_set_ratio(song.title_romanized.lower(), query.lower())

            # Do comparisons for both
            if await compare_fuzz(song, best_matches, best_fuzz_ratio, fuzz_value_translated):
                best_fuzz_ratio = fuzz_value_translated

            if await compare_fuzz(song, best_matches, best_fuzz_ratio, fuzz_value_romanized):
                best_fuzz_ratio = fuzz_value_romanized

            # Check if title matches exactly, then just set it equivalent and exit the loop
            if song.title_translated.lower() == query.lower() or song.title_romanized.lower() == query.lower():
                best_matches = [song]
                break

    return list(set(best_matches))


async def search_song_id(song_id):
    """
    search_song_id: Searches the database for a provided song_id
    :param song_id: The song_id to search the database for
    :return: Song object if it exists
             None if it does not exist
    """
    song = None
    if await database.song_exists(song_id):
        song = await database.song(song_id)

    return song


async def search_song_link(link):
    """
    search_link: Searches the database for a provided url, parsing the song_id
    :param link: The link to parse
    :return: Song object if it exists
             None if it does not exist
    """
    # Parse the ID of the song
    song_id = re.search(regex.link, link).group(1)
    return await search_song_id(song_id)


async def fetch_random(level=None):
    """
    fetch_random: Returns a random song from the database
    :return: Song object
             None if there is nothing in the database
    """
    # Fetch the full list of songs
    song_list = await database.song_list()

    # If a level is specified
    if level is not None:
        song_limited_list = []
        for song in song_list:
            if str(song.nov_level) == level or str(song.adv_level) == level or str(song.exh_level) == level or str(song.max_level) == level:
                song_limited_list.append(song)

        # If at least one song has been found, return the list
        if len(song_limited_list) > 0:
            return random.choice(song_limited_list)

        # Otherwise, return None
        else:
            return None

    # Otherwise, just fetch a random song
    else:
        # If at least one song has been found, return the list
        if len(song_list) > 0:
            return random.choice(song_list)

        # Otherwise, return None
        else:
            return None


####################
# UPDATE FUNCTIONS #
####################


async def update():
    """
    update: Updates the database, adding entries that did not previously exist
    :return: A list of errors
    """
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
        if not await database.song_add(session, song_dict):
            errors.append('Error (Add Update Song Data): ' + song_id)

    # Commit the changes and close the session
    session.commit()
    await database.session_end(session)

    return errors


async def update_song(song_id):
    """
    update_song: Fetches data to update a song and then updates it
    :param song_id: The id of the song to update
    :return: A list of any errors that may have occurred
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
    if await database.song_exists(song_id):
        if await database.song_update(session, song_dict) == False:
            errors.append('Error (Database Update Song): ' + song_id)

    else:
        print(song_dict)
        if await database.song_add(session, song_dict) == False:
            errors.append('Error (Database Add Song): ' + song_id)

    session.commit()
    await database.session_end(session)

    return errors


async def add_song(song_id):
    """
    add_song: Adds a song based on the given link
    :param song_id: The id of the song to add
    :return: A list of any errors that may have occurred
    """
    # A list of errors to keep track of
    errors = []

    # A database session in order to add songs
    session = await database.session_start()

    # Attempt to fetch the song
    song_dict = await request.song(song_id)

    # If there is an error in the dictionary
    if 'errors' in song_dict:
        # Append the error to the list of errors and then continue, "skipping" this song
        errors.append(song_dict['errors'])

    # Attempt to add to the database
    # If failed, add to errors
    if not await database.song_add(session, song_dict):
        errors.append('Error (Add Update Song Data): ' + song_id)

    # Commit the changes and close the session
    session.commit()
    await database.session_end(session)

    return errors
