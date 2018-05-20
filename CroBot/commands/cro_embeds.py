
import discord

def help():
    embed = discord.Embed(title='Commands', color=0x946b9c,
                          description='Created by Aeriq. @Aeriq if anything breaks. If he\'s not in the server, panic.\n'
                                      '!sdvxin title - Searches for title in the cached sdvx.in database\n'
                                      '!sdvxin random - Returns a random song from the sdvx.in database\n'
                                      '!sdvxin random [number] - Returns a random song from the sdvx.in database with the specified level [number]\n'
                                      '!sdvxin update - Updates the sdvx.in database; Doesn\'t overwrite existing songs\n'
                                      '!sdvxin update songTitle/songID/URL - Updates a specific song and overwrites all data for it\n'
                                      '!cro help - Returns this message')
    return embed

def github():
    embed = discord.Embed(title='Github link', color=0x946b9c,
                          description='[https://github.com/Aeriqu/CroBot](https://github.com/Aeriqu/CroBot)')
    return embed