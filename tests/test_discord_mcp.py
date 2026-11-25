import unittest
from unittest.mock import Mock

from discord_mcp import DiscordREST, validate_history_limit, validate_snowflake


class DiscordMCPHelpersTests(unittest.TestCase):
    def test_ids_must_be_numeric_snowflakes(self):
        self.assertEqual(validate_snowflake(12345, "channel_id"), "12345")
        with self.assertRaises(ValueError):
            validate_snowflake("123/../../456", "channel_id")

    def test_history_limit_is_bounded(self):
        self.assertEqual(validate_history_limit("100"), 100)
        for value in (0, 101, True, "many"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_history_limit(value)

    def test_list_text_channels_filters_non_text_channel_types(self):
        api = DiscordREST("test-token")
        api.get = Mock(
            return_value=[
                {"id": "1", "name": "general", "type": 0},
                {"id": "2", "name": "announcements", "type": 5},
                {"id": "3", "name": "voice", "type": 2},
            ]
        )

        result = api.list_text_channels("999")

        self.assertEqual(
            result,
            [
                {"id": "1", "name": "general", "type": 0},
                {"id": "2", "name": "announcements", "type": 5},
            ],
        )
        api.get.assert_called_once_with("/guilds/999/channels")

    def test_recent_messages_are_minimized_and_limit_is_forwarded(self):
        api = DiscordREST("test-token")
        api.get = Mock(
            return_value=[
                {
                    "id": "11",
                    "timestamp": "2026-01-02T03:04:05+00:00",
                    "author": {"id": "22", "username": "tester", "avatar": "omitted"},
                    "content": "hello",
                    "attachments": [
                        {
                            "filename": "file.txt",
                            "url": "https://example.test/file.txt",
                            "size": 8,
                        }
                    ],
                    "embeds": [{"title": "omitted"}],
                }
            ]
        )

        result = api.get_recent_messages("123", 7)

        self.assertEqual(
            result,
            [
                {
                    "id": "11",
                    "timestamp": "2026-01-02T03:04:05+00:00",
                    "author": {"id": "22", "username": "tester"},
                    "content": "hello",
                    "attachments": [
                        {"filename": "file.txt", "url": "https://example.test/file.txt"}
                    ],
                }
            ],
        )
        api.get.assert_called_once_with("/channels/123/messages", params={"limit": 7})


if __name__ == "__main__":
    unittest.main()
