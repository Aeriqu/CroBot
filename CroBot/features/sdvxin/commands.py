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
from CroBot.features.sdvxin import sdvx, embeds

# To keep track of db updates
sdvx_db_update = False


# Read the configuration file and fetch configuration items
config = configparser.ConfigParser()
config.read('settings.ini')
# OWNER_ID is used for overrides
OWNER_ID = config['sdvx']['owner_id']
# VOTE_TIMEOUT is used for voting purposes
# TODO: Transition voting to on reaction
VOTE_TIMEOUT = config['sdvx']['vote_timeout']
# VOTE_REQUIRED is the number of votes required to proceed
VOTE_REQUIRED = config['sdvx']['vote_required']


# Command tracker
sdvx_commands = Command('!sdvxin')

async def request(client, message):
    """
    request: Handles the request from requests.py
            Main purpose is to redirect to the proper functions
    :param client: The client we can use to send commands to discord
    :param message: The discord message to parse
    :return:
    """
    # Checks to see if there is currently an update running
    if sdvx_db_update:
        # Sends the embed stating that the update is currently ongoing within check_update()
        await client.send_message(message.channel, embed=embeds.db_update_ongoing())
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


######################
# DATABASE FUNCTIONS #
######################


@sdvx_commands.register('update')
async def update(client, message):
    """

    :param client:
    :param message:
    :return:
    """

    override = False

    return
