#
# embeds.py
# Contains all of the embeds for eamuse features
#


import discord

def maintenance(dst, maintenance_times):
    if maintenance_times is not None:
        embed = discord.Embed(title='E-Amuse Maintenance', color=0xa40000,
                              description='There is maintenance today:\n' +
                                          'JST: ' + maintenance_times[0][0] + ' - ' + maintenance_times[0][1] + '\n' +
                                          ('EST: ' if not dst else 'EDT: ') + maintenance_times[1][0] + ' - ' + maintenance_times[1][1] + '\n' +
                                          ('CST: ' if not dst else 'CDT: ') + maintenance_times[2][0] + ' - ' + maintenance_times[2][1] + '\n' +
                                          ('PST: ' if not dst else 'PDT: ') + maintenance_times[3][0] + ' - ' + maintenance_times[3][1] + '\n'
                              )

    else:
        embed = discord.Embed(title='E-Amuse Maintenance', color=0xa40000,
                              description='There is not maintenance today.')

    return embed
