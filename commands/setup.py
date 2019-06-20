import discord
from discord.ext import commands
from termcolor import cprint

from ext.table import Table


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
            def check(guild):
                return guild.name == argument
            result = discord.utils.find(check, bot.get_all_guilds())
        else:
            guild_id = int(match.group(1))
            result = bot.get_guild(guild_id)

        if not isinstance(result, discord.Guild):
            raise commands.errors.BadArgument('Channel "{}" not found.'.format(argument))

        return result


class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.text_channel_conv = commands.TextChannelConverter()

    @commands.command(aliases=['exit'])
    async def logout(self, ctx):
        '''Logs the bot out'''
        await self.bot.logout()

    @commands.command()
    async def channel(self, ctx, channel_=None, guild: GuildConverter=None):
        '''Changes channels'''
        self.bot.pause()
        Table(ctx, self.channel_callback, *[i.name for i in ctx.guild.text_channels if i.permissions_for(ctx.guild.me).read_messages]).start()

    def channel_callback(self, ctx, name):
        self.bot.channel = discord.utils.get(ctx.guild.text_channels, name=name)
        cprint('Text channel set: #{0.name} in {0.guild.name}'.format(self.bot.channel), 'green')

    @commands.command(name='help')
    async def help_(self, ctx):
        '''Shows this message'''
        cprint('\n'.join(i.name + ' - ' + i.short_doc for i in self.bot.commands), 'cyan')


def setup(bot):
    bot.add_cog(Setup(bot))
