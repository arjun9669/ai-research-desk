"""Offline checks for alert-state durability and safe Telegram formatting."""
import json
import os
import tempfile
import unittest
from unittest.mock import Mock, patch

import config
import notify
import state


class StateTests(unittest.TestCase):
    def test_roundtrip_atomic_save(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "state.json")
            with patch.object(config, "STATE_FILE", path):
                state.save_state({"BTC/USDT": "BEARISH_MACD"})
                self.assertEqual(state.load_state(), {"BTC/USDT": "BEARISH_MACD"})
                with open(path, encoding="utf-8") as f:
                    self.assertEqual(json.load(f)["BTC/USDT"], "BEARISH_MACD")

    def test_corrupt_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "state.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write("not-json")
            with patch.object(config, "STATE_FILE", path):
                self.assertEqual(state.load_state(), {})

    def test_invalid_top_level_state_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "state.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write("[]")
            with patch.object(config, "STATE_FILE", path):
                self.assertEqual(state.load_state(), {})


class NotificationTests(unittest.TestCase):
    def test_html_escapes_external_strings(self):
        message = notify.build_message(
            "Emaar <Markets>", "EMAAR.AE",
            {"bias": "bullish", "reason": "<signal>"},
            {"price": 1, "rsi": 31},
            "<b>untrusted</b>",
            [{"title": "<script>", "source": "news & data"}],
        )
        self.assertIn("Emaar &lt;Markets&gt;", message)
        self.assertIn("&lt;b&gt;untrusted&lt;/b&gt;", message)
        self.assertIn("&lt;script&gt;", message)
        self.assertIn("news &amp; data", message)

    def test_api_json_must_report_ok(self):
        with patch.object(config, "TELEGRAM_BOT_TOKEN", "fake"):
            with patch.object(config, "TELEGRAM_CHAT_ID", "fake"):
                with patch("notify.requests.post", return_value=Mock(
                    status_code=200, json=Mock(return_value={"ok": False})
                )):
                    self.assertFalse(notify.send_telegram("test"))


if __name__ == "__main__":
    unittest.main()
