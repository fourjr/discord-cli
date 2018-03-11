from discord.ext import commands

class Fun:
    def __init__(self, bot):
        self.bot = bot
    shortcuts = {
        'shrug': r'¯\\\_(ツ)\_/¯',
        'tableflip': '(╯°□°）╯︵ ┻━┻',
        'unflip': '┬─┬﻿ ノ( ゜-゜ノ)',
        'lenny': '( ͡° ͜ʖ ͡°)'
    }

    @commands.command(aliases=list(shortcuts))
    async def shortcut(self, ctx):
        await ctx.send(self.shortcuts[ctx.invoked_with])

def setup(bot):
    bot.add_cog(Fun(bot))
