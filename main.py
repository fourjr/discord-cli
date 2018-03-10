import discord
import sys
import colorama
from argparse import ArgumentParser
from termcolor import cprint
from aioconsole.stream import ainput

from commands import CommandParser

parser = ArgumentParser(description='Runs a Discord Account in the CLI.')
parser.add_argument('token', help='Your discord account/bot token')
parser.add_argument('channel', help='A single default channel you want your account to run in', type=int)
args = parser.parse_args()

bot = discord.Client()

@bot.event
async def on_ready():
    bot.channel = bot.get_channel(args.channel)
    bot.parser = CommandParser(bot)
    await bot.change_presence(status=discord.Status.offline, afk=True)
    cprint('Logged in as {0.user} in #{0.channel.name}'.format(bot), 'green')

@bot.event
async def on_connect():
    cprint('Midway through logging in.', 'green')

@bot.event
async def on_message(m):
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
    bot.run(args.token)
except discord.errors.LoginFailure:
    bot.run(args.token, self_bot=True)
