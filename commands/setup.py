import discord
import asyncio
import re
from discord.ext import commands
from termcolor import cprint

class GuildConverter(commands.IDConverter):
    '''Converts to a :class:`discord.Guild`.

    The lookup strategy is as follows (in order):
    1. Lookup by ID.
    2. Lookup by name.
    '''

    async def convert(self, ctx, argument):
        bot = ctx.bot
        result = None

        match = self._get_id_match(argument)

        if match is None:
            def check(c):
                return c.name == argument
            result = discord.utils.find(check, bot.get_all_guilds())
        else:
            guild_id = int(match.group(1))
            result = bot.get_guild(guild_id)

        if not isinstance(result, discord.Guild):
            raise commands.errors.BadArgument('Channel "{}" not found.'.format(argument))

        return result

class Setup:
    def __init__(self, bot):
        self.bot = bot
        self.text_channel_conv = commands.TextChannelConverter()

    @commands.command(aliases=['exit'])
    async def logout(self, ctx):
        await self.bot.logout()

    @commands.command()
    async def channel(self, ctx, channel_, guild: GuildConverter = None):
        if guild:
            ctx.guild = guild
        self.bot.channel = await self.text_channel_conv.convert(ctx, channel_.replace('#', ''))
        cprint('Text channel set: #{0.name} in {0.guild.name}'.format(self.bot.channel), 'green')

def setup(bot):
    bot.add_cog(Setup(bot))
