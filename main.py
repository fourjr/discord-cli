import asyncio
import sys
import os
import platform
from argparse import ArgumentParser
from collections import namedtuple

import colorama
import discord
from aioconsole.stream import ainput
from box import Box
from discord.ext import commands
from termcolor import cprint, colored

from context import Context

parser = ArgumentParser(description='Runs a Discord Account in the CLI.', usage='main.py token [-c CHANNEL] [-h]')
parser.add_argument('token', help='Your discord account/bot token')
parser.add_argument('-c', '--channel', help='A single default channel you want your account to run in', type=int)
args = parser.parse_args()

colorama.init()

## CHECKS TO ENSURE YOU DON'T TRY TO LOAD UP WITH DOWNGRADED SHIT ##
if float('.'.join(platform.python_version().split('.')[:2])) < 3.5:
    cprint('\n'.join(('You are using an unsupported version of Python.',
                      'Please upgrade to at least Python 3.5 to use discord-cli',
                      'You are currently on ' + platform.python_version())), 'red')
    exit(0)

### PROGRAM ###

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='/')
        self.loop.create_task(self.user_input())
        self.channel = None

        for i in [i.replace('.py', '') for i in os.listdir('cogs') if i.endswith('.py')]:
            self.load_extension('cogs.' + i)

        cprint('Logging in...', 'green')
        self.run()

    async def on_connect(self):
        '''Sets the client presence'''
        await self.change_presence(status=discord.Status.offline, afk=True)

    async def on_ready(self):
        '''Sets up the channel'''
        self.channel = self.get_channel(args.channel)

        if self.channel is None:
            if args.channel is not None:
                cprint('Invalid channel ID provided.', 'red')

            cprint('\n'.join(('Logged in as {0.user} in no specified channel.'.format(self),
                              'Send a channel ID to start the program')), 'green')
        else:
            cprint('Logged in as {0.user} in #{0.channel.name}'.format(self), 'green')

    async def on_message(self, m):
        await self.wait_until_ready()
        if not self.channel:
            return
        if m.channel.id == self.channel.id:
            if m.author.id == self.user.id:
                color = 'cyan'
            else:
                color = 'yellow'

            cprint('{0.author}: {0.content}'.format(m), color)

    async def user_input(self):
        '''Captures user input as a background task asynchronusly'''
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                m = await ainput()
            except EOFError:
                continue
            if m:
                ctx = await self.get_context(m)

                if ctx.channel:
                    try:

                        if ctx.command is None:
                            await self.channel.send(m)
                        else:
                            await ctx.command.invoke(ctx)

                    except discord.DiscordException as error:
                        cprint(error, 'red')

    async def get_context(self, message):
        '''Overwrites the default get_context'''

        view = commands.view.StringView(message)
        ctx = Context(view=view, bot=self, message=message)

        prefix = await self.get_prefix(message)
        invoked_prefix = prefix

        if isinstance(prefix, str):
            if not view.skip_string(prefix):
                return ctx
        else:
            invoked_prefix = discord.utils.find(view.skip_string, prefix)
            if invoked_prefix is None:
                return ctx

        invoker = view.get_word()
        ctx.invoked_with = invoker
        ctx.prefix = invoked_prefix
        ctx.command = self.all_commands.get(invoker)
        return ctx

    def run(self):
        '''Starts the bot'''
        try:
            self.loop.run_until_complete(self.start(args.token))
        except discord.errors.LoginFailure:
            try:
                super().run(args.token, bot=False)
            except discord.errors.LoginFailure:
                print('Invalid token provided.')
        finally:
            self.loop.close()

if __name__ == '__main__':
    Bot()
