# discord-cli

A small terminal client for a Discord **bot account**. Select a channel, send
messages, inspect recent history, and optionally expose read-only Discord tools
over MCP.

> This project no longer supports normal user accounts or user tokens. Discord
> [prohibits self-bots](https://support.discord.com/hc/en-us/articles/115002192352-Automated-User-Accounts-Self-Bots);
> create a bot application and use its bot token instead.

## Requirements

- Python 3.8 or later for the CLI.
- A Discord application with a bot user, installed in the server(s) it should
  access.
- The bot needs `View Channels`, `Read Message History`, and `Send Messages` in
  the channels you use. Enable **Message Content Intent** in the Developer
  Portal and in the client; Discord treats this as a privileged Gateway intent.

Install the CLI dependencies:

```sh
python -m pip install -r requirements.txt
```

## Run the CLI

Set the bot token in the environment (recommended so it is not included in the
process command line), then start the client:

```sh
export DISCORD_BOT_TOKEN="your-bot-token"
python main.py
```

On PowerShell:

```powershell
$env:DISCORD_BOT_TOKEN = "your-bot-token"
python main.py
```

You can also pass `--token`/`-t`, and optionally set an initial channel with
`--channel`/`-c`:

```sh
python main.py --channel 123456789012345678
```

## Commands

After connecting, type:

| Command | Description |
| --- | --- |
| `/guilds` | List servers the bot has joined. |
| `/channels [server-id]` | List text channels; use `/guilds` to find a server ID. |
| `/channel <channel-id>` | Select a channel. |
| `/history [1-100]` | Print recent messages from the selected channel (default: 20). |
| `/shrug`, `/tableflip`, `/unflip`, `/lenny` | Send a text shortcut. |
| `/help` | Show commands. |
| `/logout` | Disconnect. |

Any non-command line is sent as a message to the selected channel. The CLI
history command uses Discord's [Get Channel Messages
API](https://docs.discord.com/developers/resources/message#get-channel-messages)
via `discord.py` and caps each request at 100 messages. History access requires
`Read Message History`; message text may be unavailable if the bot lacks access
to message content. Do not use this client to scrape or bulk-export server data.

## Optional MCP server

The MCP bridge is a separate, **read-only** stdio server using the [official
Python SDK](https://py.sdk.modelcontextprotocol.io/). It exposes two tools:

- `list_text_channels(guild_id)` — text and announcement channels available to
  the bot.
- `get_recent_messages(channel_id, limit=20)` — up to 100 recent messages.

The bridge calls [Discord API v10](https://docs.discord.com/developers/intro)
with a bot token and the bot's own permissions;
it does not accept user credentials. Install the optional official MCP Python
SDK (Python 3.11+):

```sh
python -m pip install -r requirements-mcp.txt
```

Run `discord_mcp.py` as an MCP stdio process from your MCP host, with
`DISCORD_BOT_TOKEN` in that process's environment. For example, a local MCP
configuration can use the absolute path to this repository:

```json
{
  "mcpServers": {
    "discord-cli": {
      "command": "python",
      "args": ["/absolute/path/to/discord-cli/discord_mcp.py"],
      "env": {"DISCORD_BOT_TOKEN": "your-bot-token"}
    }
  }
}
```

Treat the MCP host as having access to the bot's channel data. Discord's API
rate limits are dynamic; the bridge observes the returned retry delay instead
of hard-coding route quotas. The bridge intentionally omits send, edit, delete,
member-list, and moderation tools. Write actions should be added only with
explicit user confirmation in the MCP host and narrow Discord permissions.

## API / MCP integration notes

The most useful initial API surfaces for this project are guild channel
discovery ([Get Guild Channels](https://docs.discord.com/developers/resources/guild#get-guild-channels))
and bounded channel history ([Get Channel Messages](https://docs.discord.com/developers/resources/message#get-channel-messages)).
They make the CLI easier to navigate and the MCP tools useful without adding
administrative side effects. The bot
must be in the target server and have visibility/history permissions. For
message text, the Message Content privileged intent must be enabled where
required. Guild/channel/message IDs are passed as IDs rather than names to
avoid ambiguous lookups.

MCP is a good fit as an optional adapter: tools mirror small Discord API
operations, while the CLI remains usable without the MCP SDK. A later extension
could add thread summaries or message search over explicitly bounded history;
Discord's API rate limits, message-content access, permission checks, and the
MCP host's user-confirmation UX should remain part of that design.

## Development

Run the offline tests with:

```sh
python -m unittest discover -s tests
```
