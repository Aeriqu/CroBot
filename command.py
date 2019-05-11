"""
command.py
Contains the command class, which contains all of the commands and their respective function entry points.
"""
from rate_limit import RateLimit


class Command(object):
    """
    The Command class keeps track of commands and their function equivalents
    """


    commands = None     # Dictionary
    starters = None     # Tuple
    rate_limit = None   # RateLimit object


    def __init__(self, starter=None):
        """
        __init__: Sets up the Command class by setting self.commands to an empty dictionary and setting the starter
        :starter: The starter for the command
        """
        self.commands = {}
        self.starters = (starter,) if starter is not None else tuple()
        self.rate_limit = RateLimit()


    def register_all(self, command):
        """
        register_all: Registers all of the commands and starters in a passed Command object to self
        :param command: The external Command object to retrieve commands from
        :return: N/A
        """
        self.commands.update(command.commands)
        self.starters += tuple(starter for starter in command.starters if starter != '')


    def register(self, argument):
        """
        register: Registers based off the command and argument passed via decorator
        :return: decorator

        Example usage:
        To register a command like !sdvxin random 19
        @command.register('random')
        def random(message_text):
            # Logic goes here

        Note: Should not be used with main Command object in run.py
        """
        def decorator(function):
            self.commands[self.starters[0] + ' ' + argument] = function
        return decorator


    async def do(self, message):
        """
        do: Runs the function based off the command
            Also checks if the user is rate limited
        :param message: The message to parse a command from and pass to the function
        :return: N/A
        """
        content = message.content
        if content.startswith(self.starters):
            # If not rate limited, register the user and then run the command
            if not await self.rate_limit.is_limited(message):

                await self.rate_limit.register(message)

                for com, func in self.commands.items():
                    if com in content:
                        await func(message)
            # If rate limited, send the limited embed
            else:
                await message.channel.send(embed=await self.rate_limit.embed_limited(message))
