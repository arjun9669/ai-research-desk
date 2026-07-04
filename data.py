# datasource.py — one interface, many markets
from typing import Protocol
import pandas as pd, yfinance as yf, ccxt

class DataSource(Protocol):
    def ohlcv(self, symbol: str) -> pd.DataFrame: ...

class YahooSource:          # DFM + ADX equities (delayed) — extends what you have
    def ohlcv(self, symbol):
        return yf.Ticker(symbol).history(period="2y", interval="1d")[["Open","High","Low","Close","Volume"]]

class CryptoSource:         # free, 24/7, genuinely real-time — the reason to add crypto
    def __init__(self, exchange="binance"): self.ex = getattr(ccxt, exchange)()
    def ohlcv(self, symbol):  # symbol like "BTC/USDT"
        raw = self.ex.fetch_ohlcv(symbol, "1d", limit=500)
        df = pd.DataFrame(raw, columns=["ts","Open","High","Low","Close","Volume"])
        return df.set_index("ts")