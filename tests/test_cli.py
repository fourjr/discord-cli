import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from main import DEFAULT_HISTORY_LIMIT, format_message, parse_history_limit


class HistoryHelpersTests(unittest.TestCase):
    def test_history_limit_defaults_to_twenty(self):
        self.assertEqual(parse_history_limit(), DEFAULT_HISTORY_LIMIT)

    def test_history_limit_accepts_discord_page_bounds(self):
        self.assertEqual(parse_history_limit("1"), 1)
        self.assertEqual(parse_history_limit("100"), 100)

    def test_history_limit_rejects_bad_values(self):
        for value in ("abc", "0", "101"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    parse_history_limit(value)

    def test_format_message_flattens_multiline_content(self):
        message = SimpleNamespace(
            created_at=datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
            author="tester",
            clean_content="first\nsecond",
            content="",
        )
        self.assertEqual(
            format_message(message),
            "[2026-01-02 03:04:05 UTC] tester: first second",
        )


if __name__ == "__main__":
    unittest.main()
