import discord
from CroBot import requests

from discord.utils import find

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    await requests.on_message(client, message)


# @client.event
# async def on_reaction_add(reaction, user):
#     # todo: add checks for sdvx.in user voting
#     print('hawa')


# Hacked in for personal server role permissions
GVM_SERVER_ID = '393603672778604544'
GVM_PLAYER_ID = '393637330700861441'
@client.event
async def on_member_join(member):
    if member.server.id == GVM_SERVER_ID:
        await client.add_roles(member, find(lambda r: r.id == GVM_PLAYER_ID, member.server.roles))


if __name__ == '__main__':
    client.run('token')