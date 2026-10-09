"""Offline tests for deterministic signal classification."""
import unittest

from signals import classify


class SignalClassificationTests(unittest.TestCase):
    def test_macd_up_takes_priority_over_rsi(self):
        value = classify({"macd_cross_up": True, "rsi": 85})
        self.assertEqual(value["label"], "BULLISH_MACD")
        self.assertEqual(value["bias"], "bullish")

    def test_macd_down(self):
        self.assertEqual(
            classify({"macd_cross_down": True})["label"], "BEARISH_MACD"
        )

    def test_golden_cross(self):
        self.assertEqual(classify({"golden_cross": True})["label"], "BULLISH_GOLDEN")

    def test_death_cross(self):
        self.assertEqual(classify({"death_cross": True})["label"], "BEARISH_DEATH")

    def test_oversold_and_overbought(self):
        self.assertEqual(classify({"rsi": 29})["label"], "BULLISH_OVERSOLD")
        self.assertEqual(classify({"rsi": 71})["label"], "BEARISH_OVERBOUGHT")

    def test_threshold_boundaries_are_neutral(self):
        self.assertEqual(classify({"rsi": 30})["label"], "NEUTRAL")
        self.assertEqual(classify({"rsi": 70})["label"], "NEUTRAL")

    def test_missing_values_are_neutral(self):
        self.assertEqual(classify({})["label"], "NEUTRAL")


if __name__ == "__main__":
    unittest.main()
