from discord.ext import commands
from termcolor import cprint

class Setup:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['exit'])
    async def logout(self, ctx):
        await self.bot.logout()

    @commands.command()
    async def channel(self, ctx, channel_id):
        try:
            self.bot.channel = self.bot.get_channel(int(channel_id))
        except ValueError:
            cprint('Invalid text channel.', 'red')
        else:
            if self.bot.channel is None:
                cprint('Invalid text channel.', 'red')
            else:
                cprint('Text channel set: #{}'.format(self.bot.channel.name), 'green')

def setup(bot):
    bot.add_cog(Setup(bot))
