import configparser
import discord
from discord.utils import get

from command import Command
# from CroBot import requests

# Create a client and command object
client = discord.Client()
command = Command()


# Register commands from features
from CroBot.features.cro.commands import cro_command
from CroBot.features.sdvxin.commands import sdvx_commands
command.register_all(cro_command)
command.register_all(sdvx_commands)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    await command.do(client, message)


# @client.event
# async def on_reaction_add(reaction, user):
#     # todo: add checks for sdvx.in user voting
#     print('hawa')


# Hacked in for personal server role permissions
GVM_SERVER_ID = 393603672778604544
@client.event
async def on_member_join(member):
    if member.guild.id == GVM_SERVER_ID:
        await member.add_roles(get(member.guild.roles, name='Players'))


if __name__ == '__main__':
    # Read in the settings file and retrieves the token
    config = configparser.ConfigParser()
    config.read('settings.ini')
    token = config['discord']['token']

    # Passes the token to the client
    client.run(token)
