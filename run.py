import discord
import commands

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
    await commands.on_message(message, client)

# Hacked in for personal server role permissions
@client.event
async def on_member_join(member):
    if member.server.id == '393603672778604544':
        await client.add_roles(member, find(lambda r: r.id == '393637330700861441', member.server.roles))


client.run('token')