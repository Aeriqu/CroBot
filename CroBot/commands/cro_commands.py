#
# cro_commands.py
# Contains all the functions needed for the Cro's functionality
#

from CroBot.commands import cro_embeds as embeds

async def request(client, message):
    if message.content == '!cro help':
        await client.send_message(message.channel, embed=embeds.help())

    elif message.content == '!cro github':
        await client.send_message(message.channel, embed=embeds.github())