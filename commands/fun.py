from discord.ext import commands

class Fun:
    '''The cog consists of fun and misc commands'''
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
        '''Command to have shortcuts such as, shrug and tableflip, sent'''
        if ctx.invoked_with == 'shortcut':
            return await ctx.send(ctx.message.content)
        await ctx.send(self.shortcuts[ctx.invoked_with])

def setup(bot):
    '''Adds the cog'''
    bot.add_cog(Fun(bot))
