import discord
import sys
import colorama
import asyncio
from argparse import ArgumentParser
from termcolor import cprint
from aioconsole.stream import ainput

from commands import CommandParser

parser = ArgumentParser(description='Runs a Discord Account in the CLI.', usage='main.py token [-c CHANNEL] [-h]')
parser.add_argument('token', help='Your discord account/bot token')
parser.add_argument('-c', '--channel', help='A single default channel you want your account to run in', type=int)
args = parser.parse_args()

bot = discord.Client()

@bot.event
async def on_connect():
    '''Just a message to show people that the system is doing stuff'''
    cprint('Midway through logging in.', 'green')

@bot.event
async def on_ready():
    '''Triggers once the bot is connected'''
    bot.channel = bot.get_channel(args.channel)
    bot.parser = CommandParser(bot)
    await bot.change_presence(status=discord.Status.offline, afk=True)
    if bot.channel is None:
        if args.channel is not None:
            cprint('Invalid channel ID provided.', 'red')

        cprint('\n'.join(('Logged in as {0.user} in no specified channel.'.format(bot),
                          'Send a channel ID to start the program')), 'green')
    else:
        cprint('Logged in as {0.user} in #{0.channel.name}'.format(bot), 'green')

@bot.event
async def on_message(m):
    await bot.wait_until_ready()
    if not bot.channel:
        return
    if m.channel.id == bot.channel.id:
        if m.author.id == bot.user.id:
            color = 'cyan'
        else:
            color = 'yellow'

        cprint('{0.author}: {0.content}'.format(m), color)

async def user_input():
    await bot.wait_until_ready()
    while not bot.is_closed():
        m = await ainput()
        if m:
            try:
                await bot.parser.parse(m)
            except discord.errors.HTTPException as e:
                cprint(e, 'red')

bot.loop.create_task(user_input())

colorama.init()

try:
    bot.loop.run_until_complete(bot.start(args.token))
except discord.errors.LoginFailure:
    try:
        bot.run(args.token, bot=False)
    except discord.errors.LoginFailure:
        print('Invalid token provided.')
finally:
    bot.loop.close()
