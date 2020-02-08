#
# commands.py
# Contains routing functions needed for eamuse functionality
#

from command import Command
from CroBot.features.eamuse import embeds
from CroBot.features.eamuse import maintenance as maint

eamuse_command = Command('!eamuse')


@eamuse_command.register('maintenance')
async def maintenance(client, message):
    """
    maintenance: Returns the times of maintenance in 4 time zones (JST, EST/EDT, CST/CDT, PST/PDT).
    :param client: Not used, sent by default from commands
    :param message: The message to reply to
    :return: N/A
    """
    await message.channel.send(embed=embeds.maintenance(
        await maint.check_dst(),
        await maint.calculate_maintenance_times()
    ))

