"""Optional, read-only MCP tools backed by Discord's official REST API."""

from __future__ import annotations

import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_BASE = "https://discord.com/api/v10"
DEFAULT_HISTORY_LIMIT = 20
MAX_HISTORY_LIMIT = 100
TEXT_CHANNEL_TYPES = {0, 5}  # Guild text and announcement channels.


class DiscordAPIError(RuntimeError):
    """Raised when Discord's API rejects or cannot complete a request."""


def validate_snowflake(value, field_name):
    """Validate a Discord snowflake before using it in a REST path."""
    value = str(value)
    if not value.isdecimal():
        raise ValueError("{0} must be a numeric Discord ID".format(field_name))
    return value


def validate_history_limit(limit=DEFAULT_HISTORY_LIMIT):
    """Validate the API's inclusive 1-100 message page size."""
    if isinstance(limit, bool):
        raise ValueError("limit must be an integer between 1 and 100")
    if isinstance(limit, float) and not limit.is_integer():
        raise ValueError("limit must be an integer between 1 and 100")
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        raise ValueError("limit must be an integer between 1 and 100")
    if not 1 <= limit <= MAX_HISTORY_LIMIT:
        raise ValueError("limit must be between 1 and 100")
    return limit


class DiscordREST:
    """Small bot-token REST client for the MCP read-only tools."""

    def __init__(self, token):
        self.token = token

    def get(self, path, params=None):
        """GET one API endpoint, honoring Discord's returned retry delay."""
        if not self.token:
            raise DiscordAPIError(
                "Set DISCORD_BOT_TOKEN before starting the MCP server"
            )
        query = "?" + urlencode(params) if params else ""
        request = Request(
            API_BASE + path + query,
            headers={
                "Authorization": "Bot " + self.token,
                "Accept": "application/json",
                "User-Agent": "discord-cli-mcp/1.0",
            },
        )
        for attempt in range(2):
            try:
                with urlopen(request, timeout=15) as response:
                    return json.loads(response.read().decode("utf-8"))
            except HTTPError as error:
                body = error.read().decode("utf-8", errors="replace")
                if error.code == 429:
                    retry_after = self._retry_delay(error, body)
                    if attempt == 0 and retry_after <= 30:
                        time.sleep(retry_after)
                        continue
                    raise DiscordAPIError(
                        "Discord rate limited this request; retry after "
                        "{0:g} seconds".format(retry_after)
                    )
                detail = self._error_message(body)
                if error.code in (401, 403, 404):
                    detail = {
                        401: "invalid bot token",
                        403: "the bot lacks permission to read this resource",
                        404: "resource not found or not visible to the bot",
                    }[error.code]
                raise DiscordAPIError(
                    "Discord API returned HTTP {0}: {1}".format(error.code, detail)
                )
            except (URLError, TimeoutError, OSError) as error:
                raise DiscordAPIError("Discord API request failed: {0}".format(error))

    @staticmethod
    def _retry_delay(error, body):
        """Read Retry-After or retry_after from the rate-limit response."""
        try:
            return (
                max(0.0, float(error.headers.get("Retry-After")))
                if error.headers
                else 1.0
            )
        except (TypeError, ValueError):
            try:
                return max(0.0, float(json.loads(body).get("retry_after", 1)))
            except (TypeError, ValueError, AttributeError, json.JSONDecodeError):
                return 1.0

    @staticmethod
    def _error_message(body):
        """Return a compact API error description without echoing credentials."""
        try:
            payload = json.loads(body)
        except (TypeError, ValueError, json.JSONDecodeError):
            return body[:300] or "request failed"
        if not isinstance(payload, dict):
            return "request failed"
        return str(payload.get("message", "request failed"))

    def list_text_channels(self, guild_id):
        """List text and announcement channels in a bot-accessible server."""
        guild_id = validate_snowflake(guild_id, "guild_id")
        channels = self.get("/guilds/{0}/channels".format(guild_id))
        return [
            {
                "id": channel["id"],
                "name": channel.get("name", ""),
                "type": channel["type"],
            }
            for channel in channels
            if channel.get("type") in TEXT_CHANNEL_TYPES
        ]

    def get_recent_messages(self, channel_id, limit=DEFAULT_HISTORY_LIMIT):
        """Return a bounded page of recent, bot-readable channel messages."""
        channel_id = validate_snowflake(channel_id, "channel_id")
        limit = validate_history_limit(limit)
        messages = self.get(
            "/channels/{0}/messages".format(channel_id),
            params={"limit": limit},
        )
        return [
            {
                "id": message.get("id"),
                "timestamp": message.get("timestamp"),
                "author": {
                    "id": message.get("author", {}).get("id"),
                    "username": message.get("author", {}).get("username"),
                },
                "content": message.get("content", ""),
                "attachments": [
                    {"filename": item.get("filename"), "url": item.get("url")}
                    for item in message.get("attachments", [])
                ],
            }
            for message in messages
        ]


def build_server(api):
    """Register Discord read-only tools on the official MCP Python SDK."""
    try:
        from mcp.server import MCPServer
    except ImportError as error:
        raise RuntimeError(
            "Install the optional MCP dependencies: pip install -r requirements-mcp.txt"
        ) from error

    server = MCPServer("discord-cli")

    @server.tool()
    def list_text_channels(guild_id: str) -> list[dict[str, object]]:
        """List a bot-accessible server's text and announcement channels by ID."""
        return api.list_text_channels(guild_id)

    @server.tool()
    def get_recent_messages(
        channel_id: str,
        limit: int = DEFAULT_HISTORY_LIMIT,
    ) -> list[dict[str, object]]:
        """Read up to 100 recent messages from a bot-accessible channel."""
        return api.get_recent_messages(channel_id, limit)

    return server


def main():
    """Run this optional MCP server over stdio."""
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        raise SystemExit(
            "Set DISCORD_BOT_TOKEN to a bot token before starting the MCP server."
        )
    server = build_server(DiscordREST(token))
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
