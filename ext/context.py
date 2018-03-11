import asyncio
import discord.abc
import discord.utils
from discord.ext import commands
from termcolor import cprint

class ConsoleMessage:
    '''
    ConsoleMessages are messages that do not appear in discord but have
    been sent through user_input and are being parsed

    This class only has 3 attributes and 0 methods:
    > content - Message Content
    > channel - Channel which the CLI is connected to
    > guild   - Guild that the CLI is connected to (if applicable)
    '''

    def __init__(self, content, bot):
        self.content = content
        self.channel = bot.channel
        self.guild = getattr(bot.channel, 'guild', False) or None

class Context(commands.Context):
    '''A CustomContext for commands parsed via user_input'''

    def __init__(self, **attrs):
        self.bot = attrs.pop('bot', None)
        self.view = attrs.pop('view', None)
        self.command = attrs.pop('command', None)
        self.message = ConsoleMessage(attrs.pop('message', None), self.bot)

        self.channel = self.bot.channel
        self.guild = getattr(self.bot.channel, 'guild', False) or None

        self.check_channel()

    def check_channel(self):
        '''Checks if channel is defined and gives error messages'''
        if self.channel is None:
            try:
                self.bot.channel = self.bot.get_channel(int(self.message.content))
            except ValueError:
                cprint('Channel not set. Send a channel ID to start the program', 'red')
            else:
                if self.bot.channel is None:
                    cprint('Invalid text channel.', 'red')
                else:
                    cprint('Text channel set: #{}'.format(self.bot.channel.name), 'green')

    async def send(self, *args, **kwargs):
        '''Replaces Messageable.send because self._state does not exist'''
        await self.channel.send(*args, **kwargs)
