"""Agent tools wrapping the existing pipeline modules. No logic duplication."""
from langchain_core.tools import tool
import config
import indicators
import news as news_mod
import signals as signals_mod
from datasource import SOURCES

_WATCH = {t: (s, n) for s, t, n in config.WATCHLIST}


@tool
def get_quote(ticker: str) -> dict:
    """Latest price + technical indicators (RSI, MACD, crossovers) for a
    watchlist ticker, e.g. 'DIB.AE' or 'BTC/USDT'."""
    entry = _WATCH.get(ticker)
    if not entry:
        return {"error": f"'{ticker}' not on watchlist: {list(_WATCH)}"}
    source_key, name = entry
    df = SOURCES[source_key].ohlcv(ticker)
    if df is None:
        return {"error": f"no data for {ticker}"}
    ind = indicators.compute_all(df)
    sig = signals_mod.classify(ind)
    return {"name": name, "indicators": ind, "signal": sig}


@tool
def run_screen() -> list[dict]:
    """Scan the full watchlist; return each symbol's current signal.
    Use to find what moved before digging into one name."""
    out = []
    for source_key, ticker, name in config.WATCHLIST:
        df = SOURCES[source_key].ohlcv(ticker)
        if df is None:
            continue
        sig = signals_mod.classify(indicators.compute_all(df))
        out.append({"ticker": ticker, "name": name,
                    "signal": sig["label"], "bias": sig["bias"]})
    return out


@tool
def fetch_news(query: str) -> list[dict]:
    """Recent headlines for ANY query you compose — company name, ticker plus
    'earnings', a sector, an event. Refine and re-query if results are thin."""
    return news_mod.fetch_headlines(query, limit=5)


TOOLS = [get_quote, run_screen, fetch_news]