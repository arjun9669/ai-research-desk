"""Analysis layer: technical indicators computed directly in pandas.

No pandas-ta dependency — that library breaks on NumPy 2.x. These implementations
are the standard formulas and have zero problematic dependencies.
"""
import pandas as pd
import config


def rsi(close: pd.Series, period: int = config.RSI_PERIOD) -> pd.Series:
    """Wilder's RSI. >70 overbought, <30 oversold."""
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    # Wilder smoothing = EWM with alpha = 1/period
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-9)
    return 100 - (100 / (1 + rs))


def macd(close: pd.Series):
    """Returns (macd_line, signal_line, histogram)."""
    ema_fast = close.ewm(span=config.MACD_FAST, adjust=False).mean()
    ema_slow = close.ewm(span=config.MACD_SLOW, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=config.MACD_SIGNAL, adjust=False).mean()
    return macd_line, signal_line, macd_line - signal_line


def sma(close: pd.Series, period: int) -> pd.Series:
    return close.rolling(window=period).mean()


def compute_all(df: pd.DataFrame) -> dict:
    """Compute every indicator and return the latest values + crossover flags."""
    close = df["Close"]

    rsi_series = rsi(close)
    macd_line, signal_line, hist = macd(close)
    sma_s = sma(close, config.SMA_SHORT)
    sma_l = sma(close, config.SMA_LONG)

    def last(series, i=-1):
        val = series.iloc[i]
        return float(val) if pd.notna(val) else None

    # Crossover = state on the most recent bar differs from the bar before it
    macd_cross_up   = last(macd_line, -2) is not None and last(macd_line) > last(signal_line) and last(macd_line, -2) <= last(signal_line, -2)
    macd_cross_down = last(macd_line, -2) is not None and last(macd_line) < last(signal_line) and last(macd_line, -2) >= last(signal_line, -2)

    golden_cross = death_cross = False
    if last(sma_l, -2) is not None and last(sma_s, -2) is not None:
        golden_cross = last(sma_s) > last(sma_l) and last(sma_s, -2) <= last(sma_l, -2)
        death_cross  = last(sma_s) < last(sma_l) and last(sma_s, -2) >= last(sma_l, -2)

    return {
        "price":          round(last(close), 3),
        "rsi":            round(last(rsi_series), 1) if last(rsi_series) is not None else None,
        "macd":           round(last(macd_line), 4) if last(macd_line) is not None else None,
        "macd_signal":    round(last(signal_line), 4) if last(signal_line) is not None else None,
        "macd_cross_up":  macd_cross_up,
        "macd_cross_down": macd_cross_down,
        "golden_cross":   golden_cross,
        "death_cross":    death_cross,
    }
