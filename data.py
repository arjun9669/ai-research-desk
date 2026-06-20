"""Data layer: pull daily price history from Yahoo Finance (free, ~15-min delayed)."""
import yfinance as yf
import pandas as pd
import config


def get_history(ticker: str) -> pd.DataFrame | None:
    """Return a clean OHLCV DataFrame for one ticker, or None if no data."""
    try:
        df = yf.Ticker(ticker).history(period=config.HISTORY_PERIOD, interval="1d")
    except Exception as e:
        print(f"[data] {ticker}: fetch error: {e}")
        return None

    if df is None or df.empty:
        print(f"[data] {ticker}: no data returned")
        return None

    # yfinance returns columns: Open High Low Close Volume Dividends Stock Splits
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    if len(df) < 30:
        print(f"[data] {ticker}: too few rows ({len(df)})")
        return None
    return df
