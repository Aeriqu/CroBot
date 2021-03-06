#
# commands.py
# Contains all the functions needed for the Cro's functionality
#

from command import Command
from CroBot.features.cro import embeds


cro_command = Command('!cro')


@cro_command.register('help')
async def help(client, message):
    """
    help: Sends the help embed information
    :param client: Not used, sent by default from commands
    :param message: The message to reply to
    :return: N/A
    """
    await message.channel.send(embed=embeds.help())


@cro_command.register('github')
async def github(client, message):
    """
    github: Sends the github embed information
    :param client: Not used, sent by default from commands
    :param message: The message to reply to
    :return: N/A
    """
    await message.channel.send(embed=embeds.github())
