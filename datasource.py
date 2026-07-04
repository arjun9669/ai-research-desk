"""Pluggable market data sources. Adding a market = adding a class here."""
from typing import Protocol
import pandas as pd
import yfinance as yf
import config


class DataSource(Protocol):
    def ohlcv(self, symbol: str) -> pd.DataFrame | None: ...


class YahooSource:
    """UAE equities (DFM/ADX via .AE/.AD suffixes). Delayed ~15 min, EOD-reliable."""

    def ohlcv(self, symbol: str) -> pd.DataFrame | None:
        try:
            df = yf.Ticker(symbol).history(period=config.HISTORY_PERIOD, interval="1d")
        except Exception as e:
            print(f"[yahoo] {symbol}: {e}")
            return None
        if df is None or df.empty or len(df) < 30:
            print(f"[yahoo] {symbol}: insufficient data")
            return None
        return df[["Open", "High", "Low", "Close", "Volume"]].dropna()


class CryptoSource:
    """Crypto via ccxt public endpoints. Free, real-time, no API key."""

    def __init__(self, exchange: str = "binance"):
        import ccxt
        self.ex = getattr(ccxt, exchange)()

    def ohlcv(self, symbol: str) -> pd.DataFrame | None:
        try:
            raw = self.ex.fetch_ohlcv(symbol, timeframe="1d", limit=500)
        except Exception as e:
            print(f"[crypto] {symbol}: {e}")
            return None
        if not raw or len(raw) < 30:
            print(f"[crypto] {symbol}: insufficient data")
            return None
        df = pd.DataFrame(raw, columns=["ts", "Open", "High", "Low", "Close", "Volume"])
        df["ts"] = pd.to_datetime(df["ts"], unit="ms")
        return df.set_index("ts")


SOURCES: dict[str, DataSource] = {
    "equity": YahooSource(),
    "crypto": CryptoSource(exchange="bybit"),
}