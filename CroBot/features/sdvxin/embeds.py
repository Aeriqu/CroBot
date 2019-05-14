#
# embeds.py
# Contains all of the embed set up for sdvx.in.
#


import re
import discord

from CroBot.features.sdvxin import regex


# Embed colors to maintain consistency
#   # General: 0x946b9c
#   # Good: 0x2ecc71
#   # In Progress: 0xe67e22
#   # Warning: 0xf1c40f
#   # Bad: 0xe74c3c


#################################
## GENERAL ERROR/INFO MESSAGES ##
#################################


def db_update_ongoing():
    """
    Returns the generic update ongoing embed message
    """
    embed = discord.Embed(title='Database updating', color=0xf1c40f,
                          description='Database is currently updating. Please wait.\n'
                                      'Please refer to the bot playing status to see if the update is still ongoing.')
    return embed


def search_not_found():
    """
    Returns the not found embed message
    """
    embed = discord.Embed(title='Search Error', color=0x946b9c,
                          description='No Song Found / Error With Query or Database')
    return embed


def search_too_many():
    """
    Returns the too many songs found embed message
    """
    embed = discord.Embed(title='Search Error', color=0xe67e22,
                          description='Too many songs found. Please refine your search.')
    return embed


def search_list(song_list):
    """
    Returns the multiple songs found embed message
    """
    msg = ''
    for song in song_list:
        msg += song.name + ' (' + song.song_id + ')\n'

    embed = discord.Embed(title='Multiple songs found.', color=0xe67e22)
    embed.add_field(name='Please enter the exact title or song id from the list below.', value=msg)
    return embed


def song(song):
    """
    song: Creates a discord embed from the passed song parameter
    :param song: The song to create an embed from
    :return: A discord embed object
    """
    # Set up an embed with the song title, color, and jacket
    embed = discord.Embed(title=song.title, color=0x946b9c)
    embed.set_thumbnail(url=song.jacket)

    description_level = ''

    # Add the novice if it exists
    if song.nov_level is not None:
        description_level += '[NOV ' + song.nov_level + '](' + song.nov_link + ') - '

    # Add the advanced if it exists
    if song.adv_level is not None:
        description_level += '[ADV ' + song.adv_level + '](' + song.adv_link + ') - '

    # Add the exhaust if it exists
    if song.exh_level is not None:
        description_level += '[EXH ' + song.exh_level + '](' + song.exh_link + ')'

    # Add the max if it exists
    if song.max_level is not None:
        # Add a continuation hyphen to match formatting
        description_level += ' - '

        # Fetch the difficulty version and then add the respective version
        version = re.search(regex.version, song.max_link).group(1)

        # If the max is inf
        if version == 'i':
            description_level += '[INF ' + song.max_level + '](' + song.max_link + ')'

        # If the max is grv
        elif version == 'g':
            description_level += '[GRV ' + song.max_level + '](' + song.max_link + ')'

        # If the max is hvn
        elif version == 'h':
            description_level += '[HVN ' + song.max_level + '](' + song.max_link + ')'

        # If the max is max / unknown
        else:
            description_level += '[MXM ' + song.max_level + '](' + song.max_link + ')'

    # Fetch the artist, if it exists
    artist = '-'
    if song.artist != '':
        artist = song.artist

    # Add the artist and the level links
    embed.add_field(name=artist, value=description_level, inline=False)

    # Add videos if they exist
    description_videos = ''

    # In game video
    if song.video_play is not None:
        description_videos += '[PLAY](' + song.video_play + ')'

    # Add a separator if in game and any of the other two exist
    if song.video_play is not None and (song.video_nofx is not None or song.video_og is not None):
        description_videos += ' - '

    # No fx video
    if song.video_nofx is not None:
        description_videos += '[NO FX](' + song.video_nofx + ')'

    # Add a separator if no fx and original exists
    if song.video_nofx is not None and song.video_og is not None:
        description_videos += ' - '

    # Original song
    if song.video_og is not None:
        description_videos += '[NO FX](' + song.video_og + ')'

    # Add the video field
    embed.add_field(name='Videos', value=description_videos)

    return embed


###################################
## UPDATE VOTE TO START MESSAGES ##
###################################


def db_update_vote_start():
    """
    Returns the general update vote embed message
    """
    embed = discord.Embed(title='Database update vote', color=0xf1c40f,
                       description='sdvx.in database update was requested.\n'
                                   'Please react 👍 to vote for an update.\n'
                                   'Database will update if 5 votes (6 reacts) are received in the next minute.')

    return embed


def db_update_song_vote_start(song=None, name=None):
    """
    Returns the start of vote update embed message
    Song is specified for existing charts
    Name is specified for new charts
    """
    embed = None
    # If a song is specified
    if song:
        embed = discord.Embed(title='Database update vote', color=0xf1c40f,
                              description='Database update requested for ' + song.name + '.\n'
                                          'Please react 👍 to vote for an update.\n'
                                          'Song will be updated if 3 votes (4 reacts) are received in the next minute.')
        embed.set_thumbnail(url=song.jacket)

    # If name is specified
    else:
        embed = discord.Embed(title='Database update vote', color=0xf1c40f, description='Database update requested for '
                                    '[' + name + '](' + name + ')\n'
                                    'Please react 👍 to vote for an update.\n '
                                    'Song will be updated if 3 votes (4 reacts) are received in the next minute.')

    return embed


###########################
## UPDATE START MESSAGES ##
###########################


def db_update_start():
    """
    Returns the generic database update started embed message
    """
    embed = discord.Embed(title='sdvx.in Update Start', color=0x946b9c,
                          description='The update for the sdvx.in db has started.\n'
                                      'Please refer to the bot playing status to see if the update is still ongoing.')
    return embed


def db_update_song_start(song=None, name=None):
    """
    Returns the song specific database update started embed message
    """
    embed = None
    if song:
        embed = discord.Embed(title='Updating: ' + song.name, color=0x946b9c,
                              description='The update for \'' + song.name + '\' has started.')
        embed.set_thumbnail(url=song.jacket)

    else:
        embed = discord.Embed(title='Updating: ' + name, color=0x946b9c,
                              description='The update for \'' + name + '\' has started.')

    return embed


##################################
## UPDATE/VOTE SUCCESS MESSAGES ##
##################################

## UPDATE MESSAGES


def db_update_success():
    """
    Returns the generic update success embed message
    """
    embed = discord.Embed(title='Database update successful', color=0x2ecc71, description='Database updated.')
    return embed


def db_update_song_success(song=None, name=None):
    """
    Returns the song specific database update success embed message
    """
    embed = None
    if song:
        embed = discord.Embed(title='Update finished for: ' + song.name, color=0xe67e22,
                              description='The update for \'' + song.name + '\' has finished.')
        embed.set_thumbnail(url=song.jacket)

    else:
        embed = discord.Embed(title='Update finished for: ' + name, color=0xe67e22,
                              description='The update for \'' + name + '\' has finished.')

    return embed


## VOTE MESSAGES


def db_update_vote_success():
    """
    Returns the general update vote successful embed message
    """
    embed = discord.Embed(title='Database update started', color=0xe67e22,
                       description='Enough votes were received.\n'
                                   'Now updating database. Please refer to the bot\'s game status for status.')

    return embed


def db_update_song_vote_success(song=None, name=None):
    """
    Returns the vote successful update embed message
    """
    embed = None
    if song:
        embed = discord.Embed(title='Database update started', color=0xe67e22,
                              description='Enough votes were received.\n'
                                          'Now updating \'' + song.name + '\'.\n'
                                          'Please refer to the bot\'s game status for status.')
        embed.set_thumbnail(url=song.jacket)

    else:
        embed = discord.Embed(title='Database update started', color=0xe67e22,
                              description='Enough votes were received.\n'
                                          'Now updating \'' + name + '\'.\n'
                                          'Please refer to the bot\'s game status for status.')

    return embed


#################################
## UPDATE/VOTE FAILED MESSAGES ##
#################################

## UPDATE MESSAGES


def db_update_failed(errors):
    """
    db_update_failed: Returns an embed with erorr information about the update
    :param errors: A list of errors
    :return: An embed with error information for a failed update
    """
    # TODO: add exception information on why it failed

    description = 'Database update failed.'

    # If there are 10 or less errors, loop through them and add to the description
    if len(errors) <= 10:
        for error in errors:
            description.join('\n' + error)

    # If there are too many errors
    else:
        description.join('\nThere were ' + str(len(errors)) + ' errors.')

    embed = discord.Embed(title='Database update failure', color=0xe74c3c,
                          description=description)
    return embed


## VOTE MESSAGES


def db_update_vote_failed(react):
    embed = discord.Embed(title='Database update vote failed', color=0xe74c3c,
                       description='Not enough votes were received. Database will not be updated. \n'
                                   'Only ' + str(react.count - 1) + ' votes were received. 5 were required.')
    return embed


def db_update_song_vote_failed(song=None, name=None, react=None):
    """
    Returns the vote failed update embed message
    """
    embed = None
    if song:
        embed = discord.Embed(title='Song update vote failed', color=0xe74c3c,
                              description='Not enough votes were received. \'' + song.name + '\' will not be updated. \n'
                                          'Only ' + str(react.count - 1) + ' votes were received. 3 were required.')

    else:
        embed = discord.Embed(title='Song update vote failed', color=0xe74c3c,
                              description='Not enough votes were received. \'' + name + '\' will not be updated. \n'
                                          'Only ' + str(react.count - 1) + ' votes were received. 3 were required.')

    return embed
