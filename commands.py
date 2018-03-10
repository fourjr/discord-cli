from termcolor import cprint

class CommandParser:

    def __init__(self, bot):
        self.bot = bot
        self.commands = ['shrug', 'channel']
        self.shortcuts = {
            'shrug': r'¯\\\_(ツ)\_/¯',
            'tableflip': '(╯°□°）╯︵ ┻━┻',
            'unflip': '┬─┬﻿ ノ( ゜-゜ノ)',
            'lenny': '( ͡° ͜ʖ ͡°)'
        }

    async def parse(self, message: str):
        if not self.bot.channel:
            if message.startswith('/exit'):
                await self.bot.logout()

            try:
                self.bot.channel = self.bot.get_channel(int(message.replace('/channel', '')))
            except ValueError:
                cprint('Channel not set. Send a channel ID to start the program', 'red')
            else:
                if self.bot.channel is None:
                    cprint('Invalid text channel.', 'red')
                else:
                    cprint('Text channel set: #{}'.format(self.bot.channel.name), 'green')
            return

        if message.startswith('/'):
            if message.startswith('/channel'):
                try:
                    self.bot.channel = self.bot.get_channel(int(message.replace('/channel', '')))
                except ValueError:
                    cprint('Invalid text channel.', 'red')
                else:
                    if self.bot.channel is None:
                        cprint('Invalid text channel.', 'red')
                    else:
                        cprint('Text channel set: #{}'.format(self.bot.channel.name), 'green')
                return

            if message.startswith('/exit'):
                await self.bot.logout()

            for item in self.shortcuts:
                message = message.replace('/' + item, self.shortcuts[item])

        await self.bot.channel.send(message)
