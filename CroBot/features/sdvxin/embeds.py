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
        msg += song.title + ' (' + song.song_id + ')\n'

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
        description_level += '[NOV ' + str(song.nov_level) + '](' + song.nov_link + ') - '

    # Add the advanced if it exists
    if song.adv_level is not None:
        description_level += '[ADV ' + str(song.adv_level) + '](' + song.adv_link + ') - '

    # Add the exhaust if it exists
    if song.exh_level is not None:
        description_level += '[EXH ' + str(song.exh_level) + '](' + song.exh_link + ')'

    # Add the max if it exists
    if song.max_level is not None:
        # If the exhaust existed, add a continuation hyphen to match formatting
        if song.exh_level is not None:
            description_level += ' - '

        # Fetch the difficulty version and then add the respective version
        version = re.search(regex.version, song.max_link).group(1)

        # If the max is inf
        if version == 'i':
            description_level += '[INF ' + str(song.max_level) + '](' + song.max_link + ')'

        # If the max is grv
        elif version == 'g':
            description_level += '[GRV ' + str(song.max_level) + '](' + song.max_link + ')'

        # If the max is hvn
        elif version == 'h':
            description_level += '[HVN ' + str(song.max_level) + '](' + song.max_link + ')'

        # If the max is max / unknown
        else:
            description_level += '[MXM ' + str(song.max_level) + '](' + song.max_link + ')'

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
        embed = discord.Embed(title='Updating: ' + song.title, color=0x946b9c,
                              description='The update for \'' + song.title + '\' has started.')
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
        embed = discord.Embed(title='Update finished for: ' + song.title, color=0xe67e22,
                              description='The update for \'' + song.title + '\' has finished.')
        embed.set_thumbnail(url=song.jacket)

    else:
        embed = discord.Embed(title='Update finished for: ' + name, color=0xe67e22,
                              description='The update for \'' + name + '\' has finished.')

    return embed


#################################
##    UPDATE FAILED MESSAGES   ##
#################################


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
