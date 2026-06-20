"""Signal layer: turn raw indicator values into ONE discrete label per stock.

A single label lets us detect when a stock's situation *changes* (so we only
alert on flips, not every run). Priority order: crossover events first (they're
rarer and more meaningful), then RSI states.
"""
import config


def classify(ind: dict) -> dict:
    """Return {'label': str, 'bias': 'bullish'|'bearish'|'neutral', 'reason': str}."""
    rsi = ind.get("rsi")

    # 1. MACD crossover (momentum shift) — highest priority
    if ind.get("macd_cross_up"):
        return {"label": "BULLISH_MACD", "bias": "bullish",
                "reason": "MACD crossed above its signal line (upward momentum)"}
    if ind.get("macd_cross_down"):
        return {"label": "BEARISH_MACD", "bias": "bearish",
                "reason": "MACD crossed below its signal line (downward momentum)"}

    # 2. Moving-average crossover (trend change)
    if ind.get("golden_cross"):
        return {"label": "BULLISH_GOLDEN", "bias": "bullish",
                "reason": "50-day average crossed above the 200-day (golden cross)"}
    if ind.get("death_cross"):
        return {"label": "BEARISH_DEATH", "bias": "bearish",
                "reason": "50-day average crossed below the 200-day (death cross)"}

    # 3. RSI extremes (overbought / oversold states)
    if rsi is not None and rsi < config.RSI_OVERSOLD:
        return {"label": "BULLISH_OVERSOLD", "bias": "bullish",
                "reason": f"RSI at {rsi} — oversold territory"}
    if rsi is not None and rsi > config.RSI_OVERBOUGHT:
        return {"label": "BEARISH_OVERBOUGHT", "bias": "bearish",
                "reason": f"RSI at {rsi} — overbought territory"}

    return {"label": "NEUTRAL", "bias": "neutral", "reason": "No notable signal"}
