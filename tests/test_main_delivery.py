"""Verify that a delivery failure does not consume a signal."""
import sys
import types
import unittest
from unittest.mock import patch

import pandas as pd

# Avoid loading live network adapters when importing the orchestration script.
fake_datasource = types.ModuleType("datasource")
fake_datasource.SOURCES = {}
with patch.dict(sys.modules, {"datasource": fake_datasource}):
    import main


class MarketData:
    def ohlcv(self, ticker):
        return pd.DataFrame({"Close": [100.0, 101.0, 102.0]})


class AlertRetryTests(unittest.TestCase):
    def run_case(self, delivered):
        signal = {"label": "BULLISH_MACD", "bias": "bullish", "reason": "MACD crossover"}
        with patch.object(main.config, "WATCHLIST", [("equity", "TEST", "Test")]), \
             patch.object(main.config, "FORCE_ALL", False), \
             patch.dict(main.SOURCES, {"equity": MarketData()}), \
             patch.object(main.state, "load_state", return_value={}), \
             patch.object(main.state, "save_state") as save, \
             patch.object(main.indicators, "compute_all", return_value={"price": 101, "rsi": 40}), \
             patch.object(main.signals, "classify", return_value=signal), \
             patch.object(main.news, "fetch_headlines", return_value=[]), \
             patch.object(main.summarize, "summarize", return_value="summary"), \
             patch.object(main.notify, "build_message", return_value="alert"), \
             patch.object(main.notify, "send_telegram", return_value=delivered):
            if delivered:
                main.run()
            else:
                with self.assertRaises(RuntimeError):
                    main.run()
            save.assert_called_once_with({"TEST": "BULLISH_MACD"} if delivered else {})

    def test_success_advances_state(self):
        self.run_case(True)

    def test_delivery_failure_retains_last_state(self):
        self.run_case(False)


if __name__ == "__main__":
    unittest.main()
