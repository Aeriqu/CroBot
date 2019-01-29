#
# sdvx_embeds.py
# Contains all of the embed set up for sdvx.in.
#

import discord

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


def song(song_list):
    """
    Returns the general song embed
    """
    # TODO: modularize further and make checks for each difficulty to support single difficulty charts; also needed for sdvx_charts.py
    # Set up embed with the song title
    embed = discord.Embed(title=song_list[0].name, color=0x946b9c)
    # Adds the jacket
    embed.set_thumbnail(url=song_list[0].jacket)

    # Adds the difficulties and the charts
    if song_list[0].max_dif is not 0:
        val = '[NOVICE](' + str(song_list[0].link_nov) + ') - [ADVANCED](' + str(
            song_list[0].link_adv) + ') - [EXHAUST](' + str(song_list[0].link_exh) + ') - '

        if song_list[0].max_dif is 1:
            val += '[INFINITE](' + str(song_list[0].link_max) + ')'
        elif song_list[0].max_dif is 2:
            val += '[GRAVITY](' + str(song_list[0].link_max) + ')'
        elif song_list[0].max_dif is 3:
            val += '[HEAVENLY](' + str(song_list[0].link_max) + ')'
        elif song_list[0].max_dif is 4:
            val += '[MAXIMUM](' + str(song_list[0].link_max) + ')'

        embed.add_field(name=song_list[0].artist, inline=False, value=val)
    else:
        embed.add_field(name=song_list[0].artist, inline=False,
                        value='[NOVICE](' + str(song_list[0].link_nov) + ') - [ADVANCED](' + str(song_list[0].link_adv) +
                           ') - [EXHAUST](' + str(song_list[0].link_exh) + ')')

    # Video field
    if song_list[0].video_play is not '' or song_list[0].video_nfx is not '' or song_list[0].video_og is not '':
        val = ''
        nam = 'Video'
        # In game video
        if song_list[0].video_play is not '':
            val += '[PLAY](' + song_list[0].video_play + ')'
        # Separator pt 1
        if song_list[0].video_play is not '' and song_list[0].video_nfx is not '':
            val += ' - '
            nam = 'Videos'
        # NOFX video
        if song_list[0].video_nfx is not '':
            val += '[NO FX](' + song_list[0].video_nfx + ')'
        # Separator pt 2 - I should find a better way to do this
        if song_list[0].video_nfx is not '' and song_list[0].video_og is not '':
            val += ' - '
            nam = 'Videos'
        # Sometimes has an other
        if song_list[0].video_og is not '':
            val += '[OTHER](' + song_list[0].video_og + ')'
        embed.add_field(name=nam, value=val)

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
    embed = discord.Embed(title='Success', color=0x2ecc71, description='Database updated.')
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


def db_update_failed():
    """
    Returns the generic update failed embed message
    """
    # TODO: add exception information on why it failed
    embed = discord.Embed(title='Failure', color=0xe74c3c,
                          description='Database update failed.')
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
