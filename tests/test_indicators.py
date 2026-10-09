"""Offline smoke tests for indicator calculations."""
import unittest

import pandas as pd

from indicators import compute_all, macd, sma


class IndicatorTests(unittest.TestCase):
    def setUp(self):
        self.close = pd.Series([float(100 + i * 0.25) for i in range(230)])

    def test_sma_matches_expected_mean(self):
        self.assertAlmostEqual(sma(self.close, 10).iloc[-1], self.close.iloc[-10:].mean())

    def test_macd_has_matching_output_lengths(self):
        line, signal, histogram = macd(self.close)
        self.assertEqual(len(line), len(self.close))
        self.assertEqual(len(signal), len(self.close))
        self.assertEqual(len(histogram), len(self.close))

    def test_compute_all_has_expected_fields(self):
        result = compute_all(pd.DataFrame({"Close": self.close}))
        self.assertEqual(
            set(result),
            {"price", "rsi", "macd", "macd_signal", "macd_cross_up",
             "macd_cross_down", "golden_cross", "death_cross"},
        )
        self.assertIsInstance(result["price"], float)
        self.assertIsInstance(result["golden_cross"], bool)


if __name__ == "__main__":
    unittest.main()
