#
# request.py
# Contains all the functions for external requests needed for sdvx.in functionality
# Functions named here are assumed that they're called such as request.x so imported calls will look clean
#

import requests


from CroBot.features.sdvxin import parse


####################
# HELPER FUNCTIONS #
####################


async def attempt_link_get(link, attempts=5):
    """
    attempt_link_get: A helper function that attempts to grab a link via GET
    :param link: The link of the site attempting to be retrieved
    :param attempts: Override of attempts, if needed. Defaults to 5.
    :return: The data requested as requests.txt if successful
             None if it was a failed attempt
    """
    # Attempt to retry on fail
    for attempt in range(attempts):
        # Attempt to get the link
        try:
            req = requests.get(link)
            return req.text
        # If it fails due to a connection or some other issue (not sure of what yet), try again until attempts are gone
        except:
            continue

    # Failed attempt
    return None


####################
#  SONG FUNCTIONS  #
####################


async def song(song_id):
    """
    song: Used to fetch data for a specific song_id
    :param song_id: The sdvx.in ID of the song
    :return: A dictionary with all information from the song
    """
    # Dictionary to hold song information
    song_dict = {'song_id': song_id}
    # Grab sort.js information and update song_dict
    song_dict.update(await song_sort(song_id))
    # Grab data.js information and update song_dict
    song_dict.update(await song_data(song_id))

    return song_dict


async def song_data(song_id):
    """
    song_data: Used to fetch the song's data.js
    Contains the following (potentially) useful information:
        - jacket information for each level (only worry about the highest leveled one)
            - Can be found in the JK[SongID][Difficulty] javascript variable
        - individual chart images (not used for this bot)
    :param song_id: The sdvx.in ID of the song
    :return: A dictionary with the value of jacket : link
             If there are any errors, errors is added to the dictionary with a list of errors that occurred
    """
    # Dictionary to hold the song's data.js information and any potential errors
    data_dict = {'jacket': ''}

    # A list to hold any potential errors
    errors = []

    # Attempt to fetch the raw javascript data
    raw_data = await attempt_link_get('http://sdvx.in/' + song_id[:2] + '/js/' + song_id + 'data.js')

    # If fetching the data was successful
    if raw_data is not None:
        try:
            data_dict['jacket'] = await parse.song_data(raw_data)
        except:
            errors.append('Error (Parse Song Data): ' + song_id)
    # If the GET request failed
    else:
        errors.append('Error (GET Song Data): ' + song_id)

    # Add errors to song_dict if there are any errors
    if len(errors) > 0:
        data_dict['errors'] = errors

    return data_dict


async def song_sort(song_id):
    """
    song_sort: Used to fetch the song's sort.js
    Contains the following (potentially) useful information (unimplemented things listed for potential features):
        - Contains the title of the song
            - Both in the comment and in the TITLE[SongID] variable (although, contains html)
        - Contains the BPM of the song (Not used for the bot)
        - Root paths to chart links and their difficulties
            - Found in variables LV[SongID][Difficulty]
        - Maximum chains per difficulty (Not used for the bot)
        - The chart effector and jacket illustrator (Not used for this bot)
        - Links to play videos (only worry about the highest level one)
            - Found in variables MV[SongID][Difficulty]
        - NoFX / Original audio videos
            - Found in SD[SongID][F/O]
    :param song_id: The sdvx.in ID of the song
    :return: A dictionary containing information from sort.js
             If there are any errors, errors is added to the dictionary with a list of errors that occurred
    """
    # Dictionary to hold the song's sort.js information and any potential errors
    sort_dict = {}

    # A list to hold any potential errors
    errors = []

    # Attempt to fetch the raw javascript data
    raw_data = await attempt_link_get('http://sdvx.in/' + song_id[:2] + '/js/' + song_id + 'sort.js')

    # If fetching the data was successful
    if raw_data is not None:
        try:
            sort_dict.update(await parse.song_sort(raw_data))
        except:
            errors.append('Error (Parse Sort Data): ' + song_id)
    # If the GET request failed
    else:
        errors.append('Error (GET Sort Data): ' + song_id)

    # Add errors to song_dict if there are any errors
    if len(errors) > 0:
        sort_dict['errors'] = errors

    return sort_dict


async def song_ids():
    """
    song_ids: Used to fetch a list of SongIDs from all of the alphabetical lists
    Alphabetical lists are used so there aren't any duplicates
    :return: A dictionary that contains a list of SongIDs under song_ids in the dictionary
             If there are any errors, errors is added to the dictionary with a list of errors that occurred
    """
    # A list of all the song lists to iterate through
    song_lists = ['http://sdvx.in/sort/sort_a.js', 'http://sdvx.in/sort/sort_k.js', 'http://sdvx.in/sort/sort_s.js',
                  'http://sdvx.in/sort/sort_t.js', 'http://sdvx.in/sort/sort_n.js', 'http://sdvx.in/sort/sort_h.js',
                  'http://sdvx.in/sort/sort_m.js', 'http://sdvx.in/sort/sort_y.js', 'http://sdvx.in/sort/sort_r.js',
                  'http://sdvx.in/sort/sort_w.js', 'http://sdvx.in/files/del.js']

    # The dictionary to hold the song_ids list (and potentially errors)
    # The reason a dictionary is used so that it can be easily seen if errors was added or not
    song_dict = {'song_ids': []}

    # A list to hold any potential errors that may occur
    # Left isolated so that it can be appended to song_dict if there are any errors. Otherwise, leave it blank
    errors = []

    # Iterate through all of the song lists
    for list in song_lists:
        # Attempt to fetch raw javascript data
        raw_data = await attempt_link_get(list)
        # Checks to see if the fetching was successful to some degree
        if raw_data is not None:
            try:
                song_dict['song_ids'] += await parse.song_ids(raw_data)
            except:
                errors.append('Error (Parse SongID List): ' + list)
        # If the GET request failed
        else:
            errors.append('Error (GET SongID List): ' + list)

    # Add errors to song_dict if there are any errors
    if len(errors) > 0:
        song_dict['errors'] = errors

    return song_dict
