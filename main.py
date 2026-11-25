"""A small, bot-account-only Discord terminal client."""

import argparse
import asyncio
import os
import shlex

import colorama
import discord
from aioconsole.stream import ainput
from termcolor import cprint


DEFAULT_HISTORY_LIMIT = 20
MAX_HISTORY_LIMIT = 100


def parse_history_limit(value=None):
    """Return a valid Discord message-history limit (1-100)."""
    if value is None:
        return DEFAULT_HISTORY_LIMIT
    try:
        limit = int(value)
    except (TypeError, ValueError):
        raise ValueError("history limit must be an integer between 1 and 100")
    if not 1 <= limit <= MAX_HISTORY_LIMIT:
        raise ValueError("history limit must be between 1 and 100")
    return limit


def format_message(message):
    """Format one Discord message for the terminal."""
    timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
    content = message.clean_content or message.content or "[no text content]"
    content = content.replace("\r", " ").replace("\n", " ")
    return "[{0}] {1}: {2}".format(timestamp, message.author, content)


class Bot(discord.Client):
    """Connect a bot account and provide a line-oriented terminal UI."""

    shortcuts = {
        "shrug": r"¯\\\_(ツ)\_/¯",
        "tableflip": "(╯°□°）╯︵ ┻━┻",
        "unflip": "┬─┬﻿ ノ( ゜-゜ノ)",
        "lenny": "( ͡° ͜ʖ ͡°)",
    }

    def __init__(self, channel_id=None):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.channel_id = channel_id
        self.channel = None
        self.input_task = None

    async def setup_hook(self):
        """Start the interactive input task after the client is initialized."""
        self.input_task = asyncio.create_task(self.user_input())

    async def on_ready(self):
        """Resolve an optional starting channel and show the bot identity."""
        if self.user is not None:
            cprint("Logged in as {0} (bot account).".format(self.user), "green")
        if self.channel_id is not None:
            await self.set_channel(self.channel_id)
        cprint(
            "Type /help for commands. Messages are sent to the selected channel.",
            "cyan",
        )

    async def on_message(self, message):
        """Print incoming and outgoing messages from the selected channel."""
        if self.channel is None or message.channel.id != self.channel.id:
            return
        color = "cyan" if self.user and message.author.id == self.user.id else "yellow"
        cprint(format_message(message), color)

    async def close(self):
        """Stop the input loop before closing the Discord connection."""
        current_task = asyncio.current_task()
        if (
            self.input_task is not None
            and self.input_task is not current_task
            and not self.input_task.done()
        ):
            self.input_task.cancel()
        await super().close()

    async def set_channel(self, channel_id):
        """Select a channel by its Discord snowflake ID."""
        try:
            channel_id = int(channel_id)
        except (TypeError, ValueError):
            cprint("Channel ID must be an integer.", "red")
            return False

        channel = self.get_channel(channel_id)
        if channel is None:
            try:
                channel = await self.fetch_channel(channel_id)
            except (
                discord.NotFound,
                discord.Forbidden,
                discord.HTTPException,
            ) as error:
                cprint("Could not access channel: {0}".format(error), "red")
                return False

        if not isinstance(channel, discord.abc.Messageable):
            cprint("That channel cannot receive messages.", "red")
            return False

        self.channel = channel
        self.channel_id = channel_id
        cprint("Selected channel {0} ({1}).".format(channel, channel_id), "green")
        return True

    def list_guilds(self):
        """Print guilds visible to the bot over the Gateway."""
        if not self.guilds:
            cprint("The bot is not connected to any servers.", "yellow")
            return
        for guild in sorted(self.guilds, key=lambda item: item.name.casefold()):
            cprint("{0}  {1}".format(guild.id, guild.name), "cyan")

    def list_channels(self, guild_id=None):
        """Print readable text channels, optionally scoped to a guild ID."""
        if guild_id is None and self.channel is not None:
            guild = getattr(self.channel, "guild", None)
        else:
            try:
                guild = self.get_guild(int(guild_id))
            except (TypeError, ValueError):
                guild = None
        if guild is None:
            cprint("Use /channels <server-id> or /guilds to find a server.", "yellow")
            return
        channels = [channel for channel in guild.text_channels]
        if not channels:
            cprint(
                "No text channels are available in {0}.".format(guild.name), "yellow"
            )
            return
        for channel in channels:
            cprint("{0}  #{1}".format(channel.id, channel.name), "cyan")

    async def show_history(self, limit=None):
        """Print recent messages from the selected channel, oldest first."""
        if self.channel is None:
            cprint("Select a channel first with /channel <channel-id>.", "red")
            return
        try:
            limit = parse_history_limit(limit)
        except ValueError as error:
            cprint(str(error), "red")
            return
        try:
            messages = [message async for message in self.channel.history(limit=limit)]
        except (discord.Forbidden, discord.HTTPException) as error:
            cprint("Could not read channel history: {0}".format(error), "red")
            return
        if not messages:
            cprint("No messages found.", "yellow")
            return
        for message in reversed(messages):
            color = (
                "cyan" if self.user and message.author.id == self.user.id else "yellow"
            )
            cprint(format_message(message), color)

    async def handle_command(self, text):
        """Run a local command; incoming Discord messages are never commands."""
        try:
            parts = shlex.split(text[1:])
        except ValueError as error:
            cprint("Could not parse command: {0}".format(error), "red")
            return
        if not parts:
            return

        name, *arguments = parts
        name = name.casefold()
        if name == "help":
            cprint(
                "\n".join(
                    (
                        "/guilds - list servers the bot has joined",
                        "/channels [server-id] - list text channels",
                        "/channel <channel-id> - select a channel",
                        "/history [1-100] - show recent messages (default 20)",
                        "/shrug, /tableflip, /unflip, /lenny - send a shortcut",
                        "/logout - disconnect",
                        "Any other line is sent as a message to the selected channel.",
                    )
                ),
                "cyan",
            )
        elif name == "guilds":
            self.list_guilds()
        elif name == "channels":
            if len(arguments) > 1:
                cprint("Usage: /channels [server-id]", "red")
            else:
                self.list_channels(arguments[0] if arguments else None)
        elif name == "channel":
            if len(arguments) != 1:
                cprint(
                    "Usage: /channel <channel-id> (use /channels to list channels)",
                    "red",
                )
            else:
                await self.set_channel(arguments[0])
        elif name == "history":
            if len(arguments) > 1:
                cprint("Usage: /history [1-100]", "red")
            else:
                await self.show_history(arguments[0] if arguments else None)
        elif name in self.shortcuts:
            if arguments:
                cprint("Usage: /{0}".format(name), "red")
            else:
                await self.send_message(self.shortcuts[name])
        elif name == "logout":
            await self.close()
        else:
            cprint("Unknown command. Type /help for the command list.", "red")

    async def send_message(self, content):
        """Send text to the selected channel."""
        if self.channel is None:
            cprint("Select a channel first with /channel <channel-id>.", "red")
            return
        try:
            await self.channel.send(content)
        except (discord.Forbidden, discord.HTTPException) as error:
            cprint("Could not send message: {0}".format(error), "red")

    async def user_input(self):
        """Read terminal input asynchronously and route commands/messages."""
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                text = (await ainput("> ")).strip()
            except (EOFError, asyncio.CancelledError):
                if not self.is_closed():
                    await self.close()
                return
            if not text:
                continue
            if text.startswith("/"):
                await self.handle_command(text)
            elif self.channel is None and text.isdecimal():
                await self.set_channel(text)
            else:
                await self.send_message(text)


def build_parser():
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Run a Discord bot account in the CLI."
    )
    parser.add_argument(
        "-t", "--token", help="Discord bot token (or set DISCORD_BOT_TOKEN)"
    )
    parser.add_argument("-c", "--channel", type=int, help="Optional initial channel ID")
    return parser


def main():
    """Start the bot-only terminal client."""
    colorama.init()
    parser = build_parser()
    args = parser.parse_args()
    token = args.token or os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        parser.error("provide a bot token with --token or DISCORD_BOT_TOKEN")
    try:
        Bot(channel_id=args.channel).run(token)
    except discord.LoginFailure:
        cprint("Invalid bot token. User account tokens are not supported.", "red")


if __name__ == "__main__":
    main()
