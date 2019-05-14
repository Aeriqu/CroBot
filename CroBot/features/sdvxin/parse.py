#
# parse.py
# Uses the regexps in regex.py to parse out needed information
# Functions named here are assumed that they're called such as parse.x so imported calls will look clean
#


import re
import html
import unidecode


from CroBot.features.sdvxin import regex, translate


async def song_ids(raw_data):
    """
    song_ids: Parses an alphabetic listing of songs and returns a list of SongIDs
    :param raw_data: Raw javascript data, with lots of html in it (the true joy of making a program for this site. oh no.)
    :return: A list of SongIDs
    """
    # The list of SongIDs to be sent back
    song_ids = []

    # Make the raw data iterable for use
    iterable_data = raw_data.split('\n')
    # Iterate through the data
    for line in iterable_data:
        # Check to see if the line includes a SongID
        if re.search(regex.id_parse, line) is not None:
            # Fetch the song_id
            song_id = re.search(regex.id_parse, line).group(1)
            # Append song_ids to song_id
            song_ids.append(song_id)

    return song_ids


async def song_data(raw_data):
    """
    song_data: Parses through a song's data.js to obtain the jacket information
    :param raw_data: The raw javascript data
    :return: The jacket link
    """
    # The jacket link to be sent back
    jacket = ''

    # Make the raw data iterable for use
    iterable_data = raw_data.split('\n')
    # Iterate through the data and find the last jacket
    for line in iterable_data:
        # If a jacket was found
        if re.search(regex.jacket, line) is not None:
            # Set to jacket
            jacket = 'http://sdvx.in'+re.search(regex.jacket, line).group(1)

    return jacket


async def song_sort(raw_data):
    """
    song_sort: Parses through a song's sort.js to obtain a majority of the needed information
    :param raw_data: The raw javascript data
    :return: A dictionary containing all of the information
    """
    # A dictionary to hold all of the sort data
    sort_dict = {}

    # Make the raw data iterable for use
    iterable_data = raw_data.split('\n')

    # List of lines to skip, filled by helper functions as they use lines
    skip_list = [0]

    # Grab the title of the chart
    title = await sort_title(iterable_data)
    sort_dict.update(title)
    # TODO: Add error checking for title
    # {'song_id': '04378', 'title': 'ファイナルレター', 'title_translated': 'Error 401000: The request is not authorized because credentials are missing or invalid.', 'title_pronunciation': 'Error 401000: The request is not authorized because credentials are missing or invalid.', 'artist': '', 'nov_link': 'http://sdvx.in/04/04378n.htm', 'nov_level': '06', 'adv_level': '12', 'adv_link': 'http://sdvx.in/04/04378a.htm', 'exh_level': '16', 'exh_link': 'http://sdvx.in/04/04378e.htm', 'max_level': '18', 'max_link': 'http://sdvx.in/04/04378m.htm', 'video_play': 'https://www.youtube.com/watch?v=WMsPky3YQRQ', 'video_nofx': 'https://www.youtube.com/watch?v=wQiPB9V8a38', 'jacket': 'http://sdvx.in/04/jacket/04378m.png'}

    # Grab the artist of the song
    artist = await sort_artist(iterable_data, skip_list)
    sort_dict.update(artist['data'])
    skip_list += artist['lines']

    # Grab all of the difficulties then update the dictionary and skip_list accordingly
    difficulties = await sort_difficulties(iterable_data, skip_list)
    sort_dict.update(difficulties['data'])
    skip_list += difficulties['lines']

    # Grab all of the videos then update the dictionary and skip_list accordingly
    videos = await sort_videos(iterable_data, skip_list)
    sort_dict.update(videos['data'])
    skip_list += videos['lines']


    return sort_dict


##############################
# song_sort HELPER FUNCTIONS #
##############################


async def sort_title(iterable_data):
    """
    sort_title: Fetches title information from iterable_data, although just the first line.
    :param iterable_data: The data needed to find the title
    :return: A dictionary containing the title, translated title, and pronunciation of title
    """
    # Dictionary containing the title
    title_dict = {'title': {}}
    # Fetch the first line to grab title information
    line = iterable_data[0]
    # Parse the title from the line
    # Removes any html tags and decodes any html characters
    title = re.sub(r'<[^<]+?>', '', html.unescape(re.search(regex.title, line).group(2)))
    title_dict['title'] = title

    # If the title contains Japanese text to be translated
    if re.search(regex.japanese, title) is not None:

        # Obtain the English translation
        title_dict['title_translated'] = await translate.translate(title)


        # Obtain the Japanese pronunciation
        title_dict['title_romanized'] = await translate.transliterate(title)

    # If the title does not contain Japanese
    else:
        # Set both title_translated and title_pronunciation to the original title for database purposes
        title_dict['title_translated'] = title
        title_dict['title_romanized'] = title

    return title_dict


async def sort_artist(iterable_data, skip_list):
    """
    sort_artist: Used to parse out the artist of the song from sort.js
    :param iterable_data: The data needed to iterate through to find the artist
    :param skip_list: The list of lines to be skipped since they were used for other purposes
    :return: A dictionary containing the artist information and lines used
    """
    # Dictionary containing data and new lines to be passed back
    # artist is predefined in data in the case that the artist line does not exist
        # Usually the case for new charts
    artist_dict = {'data': {'artist': '-'}, 'lines': []}

    # Iterate through the data and find the artist information
    for line_number, line in enumerate(iterable_data):
        # If the line should be skipped, then skip it
        if line_number in skip_list:
            continue

       # If the artist line is found
        if re.search(regex.artist, line) is not None:
            artist_dict['lines'].append(line_number)
            artist_dict['data']['artist'] = html.unescape(re.search(regex.artist, line).group(1))
            break

    return artist_dict


async def sort_difficulties(iterable_data, skip_list):
    """
    sort_difficulties: Used to parse out all of the difficulties and their values from sort.js
    :param iterable_data: The data needed to iterate through to find the difficulties
    :param skip_list: The list of lines to be skipped since they were used for other purposes
    :return: A dictionary containing all of the difficulty information and lines used, so they may be skipped
    """
    # Dictionary containing data and new lines to be skipped to be passed back
    difficulties_dict = {'data': {}, 'lines': []}

    # Iterate through the data and find the the difficulty information
    for line_number, line in enumerate(iterable_data):
        # If the line should be skipped, then skip it
        if line_number in skip_list:
            continue

        # If the line contains the general difficulty information
        if re.search(regex.dif_general, line) is not None:
            # Make sure that we aren't on any of the sort lines
            if re.search(regex.sort_exclude, line) is None and re.search(regex.dif_level, line):
                # Guaranteed addition, add the line to the list of lines to skip
                difficulties_dict['lines'].append(line_number)
                # If the line is the novice difficulty
                if re.search(regex.dif_nov, line) is not None:
                    # Add the novice chart's level and link to the dictionary
                    difficulties_dict['data']['nov_link'] = 'http://sdvx.in' + re.search(regex.dif_link, line).group(0)
                    # In the case of it being a joke chart, such as grace's tutorial, sdvx.in will not have a difficulty number.
                    # However, this is the only case of this happening, so we'll leave it as 1
                    try:
                        difficulties_dict['data']['nov_level'] = re.search(regex.dif_level, line).group(1)
                    except:
                        difficulties_dict['data']['nov_level'] = '1'

                # If the line is the advanced difficulty
                elif re.search(regex.dif_adv, line) is not None:
                    # Add the advanced chart's level and link to the dictionary
                    difficulties_dict['data']['adv_level'] = re.search(regex.dif_level, line).group(1)
                    difficulties_dict['data']['adv_link'] = 'http://sdvx.in' + re.search(regex.dif_link, line).group(0)
                # If the line is the exhaust difficulty
                elif re.search(regex.dif_exh, line) is not None:
                    # Add the exhaust chart's level and link to the dictionary
                    difficulties_dict['data']['exh_level'] = re.search(regex.dif_level, line).group(1)
                    difficulties_dict['data']['exh_link'] = 'http://sdvx.in' + re.search(regex.dif_link, line).group(0)
                # If the line is the max difficulty
                elif re.search(regex.dif_max, line) is not None:
                    # Add the max chart's level and link to the dictionary
                    difficulties_dict['data']['max_level'] = re.search(regex.dif_level, line).group(1)
                    difficulties_dict['data']['max_link'] = 'http://sdvx.in' + re.search(regex.dif_link, line).group(0)
                    # Add the maximum type
                    # Not needed, just parse from URL. TODO: REMOVE THIS COMMENT AFTER IMPLEMENTATION

    return difficulties_dict


async def sort_videos(iterable_data, skip_list):
    """
    sort_videos: Used to parse out all of the videos and their values from sort.js
    :param iterable_data: The data needed to iterate through to find the difficulties
    :param skip_list: The list of lines to be skipped since they were used for other purposes
    :return: A dictionary containing all of the video information and lines used, so they may be skipped
    """
    # Dictionary containing data and new lines to be skipped to be passed back
    videos_dict = {'data': {}, 'lines': []}

    # Iterate through the data and find the the difficulty information
    for line_number, line in enumerate(iterable_data):
        # If the line should be skipped, then skip it
        if line_number in skip_list:
            continue

        # If the line contains a music type
        if re.search(regex.video_music, line) is not None:
            # If there is a link in the line
            if re.search(regex.video_link, line) is not None:
                # Add the line to the skip list
                videos_dict['lines'].append(line_number)
                # If the music video is a nofx video
                if re.search(regex.video_nofx, line) is not None:
                    # Add the nofx video link to the dictionary
                    videos_dict['data']['video_nofx'] = re.search(regex.video_link, line).group(1)
                # If the music video is an original video
                elif re.search(regex.video_og, line) is not None:
                    # Add the original video link to the dictionary
                    videos_dict['data']['video_og'] = re.search(regex.video_link, line).group(1)

        # If the line contains a play type
        elif re.search(regex.video_play, line) is not None:
            # If there is a link in the line
            if re.search(regex.video_link, line) is not None:
                # Add the line to the skip list
                videos_dict['lines'].append(line_number)
                videos_dict['data']['video_play'] = re.search(regex.video_link, line).group(1)

    return videos_dict

