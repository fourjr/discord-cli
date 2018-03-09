import discord
import sys
import colorama
from argparse import ArgumentParser
from termcolor import colored, cprint


parser = ArgumentParser(description='Runs a Discord Account in the CLI.')
parser.add_argument('token', help='Your discord account/bot token')
parser.add_argument('channel', help='A single default channel you want your account to run in')
args = parser.parse_args()

bot = discord.Client()

@bot.event
async def on_ready():
    cprint(f'Logged in as {bot.user}', 'green')
    bot.channel = bot.get_channel(args.channel)

@bot.event
async def on_message(m):
    if m.channel.id == args.channel:
        if m.author.id == bot.user.id:
            color = 'cyan'
        else:
            color = 'yellow'

        cprint(f'{m.author}: {m.content}', color)

async def user_input():
    await bot.wait_until_ready()
    while not bot.is_closed():
        m = input()
        if m:
            try:
                await bot.channel.send(m)
            except discord.errors.HTTPException as e:
                cprint(e, 'red', 'on_white')

bot.loop.create_task(user_input())
colorama.init()

try:
    bot.run(args.token)
except discord.errors.LoginFailure:
    bot.run(args.token, self_bot=True)
