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
        '''Command to have shrug tableflip etc sent'''
        if ctx.invoked_with == 'shortcut':
            return await ctx.send(ctx.message.content)
        await ctx.send(self.shortcuts[ctx.invoked_with])

def setup(bot):
    bot.add_cog(Fun(bot))
