#
# requests.py
# Manages the timeout dictionary and routes the commands to the proper command module
#


from CroBot.features.sdvxin import commands as sdvx
from CroBot.features.cro import commands as cro

import time

from collections import defaultdict

# Timeout setup
INTERVAL = 5
# format: name, time able to talk
timeoutDict = defaultdict(float)

# Embed colors
#   # General: 0x946b9c
#   # Good: 0x2ecc71
#   # In Progress: 0xe67e22
#   # Warning: 0xf1c40f
#   # Bad: 0xe74c3c

# Messages
async def on_message(client, message):
    global timeoutList
    global sdvxDBUpdate

    commandList = ('!sdvxin', '!cro')

    if message.content.startswith(commandList):


        ## TIMEOUT


        now = time.time()
        # remove all users who have completed timeout
        for user, timeAvailable in list(timeoutDict.items()):
            if timeAvailable <= now:
                del timeoutDict[user]
        # if user still exists, their timeout hasn't finished
        if message.author.id in timeoutDict:
            return
        # add user to list and start query
        timeoutDict[message.author.id] = now + INTERVAL


        ## SDVX.IN


        if message.content.startswith('!sdvxin'):
            # Sends the request over to sdvx
            await sdvx.request(client, message)


        ## CRO


        # For bot specific commands
        elif message.content.startswith('!cro'):
            await cro.request(client, message)