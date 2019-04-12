import configparser
import discord

from command import Command
# from CroBot import requests

# Create a client and command object
client = discord.Client()
command = Command()


# Register commands from features
from CroBot.features.cro.commands import cro_command
command.register_all(cro_command)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    await command.do(message)


# @client.event
# async def on_reaction_add(reaction, user):
#     # todo: add checks for sdvx.in user voting
#     print('hawa')


# Hacked in for personal server role permissions
# GVM_SERVER_ID = '393603672778604544'
# GVM_PLAYER_ID = '393637330700861441'
# @client.event
# async def on_member_join(member):
#     if member.server.id == GVM_SERVER_ID:
#         await client.add_roles(member, find(lambda r: r.id == GVM_PLAYER_ID, member.server.roles))


if __name__ == '__main__':
    # Read in the settings file and retrieves the token
    config = configparser.ConfigParser()
    config.read('settings.ini')
    token = config['discord']['token']

    # Passes the token to the client
    client.run(token)
