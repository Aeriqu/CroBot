"""
rate_limit.py
Contains the rate limit class and related features
"""
import time
import configparser
from collections import defaultdict

import discord


class RateLimit(object):


    # timeout_dict formatted as: user_id: time_available (when user can message again)
    timeout_dict = None
    # timeout time
    TIMEOUT_TIME = None


    def __init__(self):
        self.timeout_dict = defaultdict(float)
        # Open the configuration file to get the timeout
        config = configparser.ConfigParser()
        config.read('settings.ini')
        self.TIMEOUT_TIME = int(config['discord']['command_timeout'])


    async def clear_old(self):
        """
        clear_old: Clears out all of the old entries in self.timeout_dict
        :return: N/A
        """
        # Fetch the current time
        time_now = time.time()
        # Loop through the the times and see what can be removed
        for user_id, time_available in list(self.timeout_dict.items()):
            if time_available <= time_now:
                del self.timeout_dict[user_id]


    async def is_limited(self, message):
        """
        is_limited: Checks to see if the user is currently being rate limited.
                    - Also calls clear_old() to get rid of any old items
        :param message: The message to look for the user
        :return: N/A
        """
        # Clear out the old list
        await self.clear_old()

        # Check if the user is still in the timeout list
        if str(message.author.id) in self.timeout_dict:
            return True
        # If the user is not in the timeout list
        return False


    async def register(self, message):
        """
        register: Registers a user in the dictionary for rate limiting
        :param message: The message to obtain the user
        :return: N/A
        """
        self.timeout_dict[str(message.author.id)] = time.time() + self.TIMEOUT_TIME


    async def embed_limited(self, message):
        """
        embed_limited: Returns an embed stating the user has been rate limited.
        :param message: The message to obtain the user
        :return:
        """
        embed = discord.Embed(title='Rate Limited', color=0x946b9c,
                              description='You (' + message.author.name + ') are currently rate limited. Please wait.\n'
                                          'The current rate limit is ' + str(self.TIMEOUT_TIME) + ' seconds.')
        return embed