import asyncio
import aiohttp
import json
import os
import platform
import re
from argparse import ArgumentParser
from getpass import getpass

import colorama
import discord
import requests
from aioconsole.stream import ainput
from discord.ext import commands
from termcolor import cprint

from ext.context import Context

parser = ArgumentParser(description='Runs a Discord Account in the CLI.', usage='main.py token [-c CHANNEL] [-h]')
parser.add_argument('-t', '--token', help='Your discord account/bot token')
parser.add_argument('-c', '--channel', help='A single default channel you want your account to run in', type=int)
args = parser.parse_args()

colorama.init()

# PROGRAM #

class Bot(commands.Bot):
    '''Bot subclass to handle CLI IO'''
    def __init__(self):
        intents = discord.Intents.all()  # Ensure intents are set here
        super().__init__(command_prefix='/', intents=intents)
        self.channel = None
        self.is_bot = None
        self.paused = False
        self.role_converter = commands.RoleConverter()
        self.member_converter = commands.MemberConverter()
        self.remove_command('help')

        cprint('Logging in...', 'green')

    async def setup(self):
        self.session = aiohttp.ClientSession()  # Create session in async context

        # Load extensions asynchronously
        for i in [i.replace('.py', '') for i in os.listdir('commands') if i.endswith('.py')]:
            await self.load_extension('commands.' + i)

        asyncio.create_task(self.user_input())  # Use asyncio.create_task to create tasks asynchronously
        await self.start(args.token)

    async def on_connect(self):
        '''Sets the client presence'''
        self.is_bot = self._connection.is_bot
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
            cprint('Logged in as {0.user} in #{0.channel}'.format(self), 'green')

    async def on_message(self, message):
        '''Prints to console upon new message'''
        await self.wait_until_ready()
        if not self.channel or self.paused:
            return
        if message.channel.id == self.channel.id:
            if message.author.id == self.user.id:
                color = 'cyan'
            else:
                color = 'yellow'

            match = [i.group(0) for i in re.finditer(r'<(@(!?|&?)|#)([0-9]+)>', message.content)]
            if match:
                for mention in match:
                    mention_id = int(
                        mention
                        .replace('<@', '')
                        .replace('>', '')
                        .replace('!', '')
                        .replace('&', '')
                        .replace('<#', '')
                    )

                    def check(role):
                        return role.id == mention_id
                    result = self.get_user(mention_id) or discord.utils.find(check, message.guild.roles) or self.get_channel(mention_id)
                    message.content = message.content.replace(mention, '@{}'.format(result))

            cprint('{0.author}: {0.content}'.format(message), color)

    async def user_input(self):
        '''Captures user input as a background task asynchronusly'''
        await self.wait_until_ready()
        while not self.is_closed():
            if self.paused:
                continue
            try:
                text = await ainput()
            except EOFError:
                continue
            if text:
                ctx = await self.get_context(text)

                # MENTION CONVERT #
                match = [i.group(1).strip() for i in re.finditer(r'@([^ @]+)', text)]
                if match:
                    for mention in match:
                        try:
                            result = await self.member_converter.convert(ctx, mention)
                        except commands.errors.BadArgument:
                            try:
                                result = await self.role_converter.convert(ctx, mention)
                            except commands.errors.BadArgument:
                                result = None

                        if result is not None:
                            text = text.replace('@' + mention, result.mention)

                # END OF MENTION CONVERT #

                if ctx.channel:
                    try:
                        if ctx.command is None:
                            await self.channel.send(text)
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

    async def close(self):
        await self.session.close()
        await super().close()

    def run(self):
        asyncio.run(self.setup())  # Run the setup with asyncio

if __name__ == '__main__':
    Bot().run()
