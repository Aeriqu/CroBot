import discord

import re
import sdvxCharts
INTERVAL = 30
last_command_time = 0

async def on_message(message, client):
    global last_command_time
    # sdvx.in functionality
    if message.content.startswith('!sdvxin'):
        now = time.time()
        if now - last_command_time < INTERVAL:
            return
        last_command_time = now
        name = re.search(r'(!sdvxin\s)(.*)', message.content).group(2)
        try:
            songList = sdvxCharts.query(name)
        except Exception as e:
            print('sdvx error: '+name+' '+e)

        if len(songList) is 1:
            # Set up embed
            em = discord.Embed(title=songList[0].name, color=0x946b9c)
            if songList[0].maxDif is not 0:
                val = '[NOVICE]('+str(songList[0].linkNov)+') - [ADVANCED]('+str(songList[0].linkAdv)+') - [EXHAUST]('+str(songList[0].linkExh)+') - '

                if songList[0].maxDif is 1:
                    val += '[INFINITE]('+str(songList[0].linkMax)+')'
                elif songList[0].maxDif is 2:
                    val += '[GRAVITY](' + str(songList[0].linkMax) + ')'
                elif songList[0].maxDif is 3:
                    val += '[HEAVENLY](' + str(songList[0].linkMax) + ')'
                elif songList[0].maxDif is 4:
                    val += '[MAXIMUM](' + str(songList[0].linkMax) + ')'

                em.add_field(name='-', value=val)
            else:
                em.add_field(name='-', value='[NOVICE]('+str(songList[0].linkNov)+') - [ADVANCED]('+str(songList[0].linkAdv)+') - [EXHAUST]('+str(songList[0].linkExh)+')')

            await client.send_message(message.channel, embed=em)
        elif len(songList) is 0:
            await client.send_message(message.channel, 'No Song Found / Error With Query')
        else:
            await client.send_message(message.channel, 'Multiple songs found with that request. I\'ll add this later')
