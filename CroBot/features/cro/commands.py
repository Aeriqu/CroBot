#
# commands.py
# Contains all the functions needed for the Cro's functionality
#

from command import Command
from CroBot.features.cro import embeds


cro_command = Command('!cro')


@cro_command.register('help')
async def help(message):
    await message.channel.send(embed=embeds.help())


@cro_command.register('github')
async def github(message):
    await message.channel.send(embed=embeds.github())