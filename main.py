"""AI Market Research Desk — main pipeline.

Run:  python main.py
For the first demo (alert on every symbol):  FORCE_ALL=true python main.py
"""
import config
import indicators
import signals
import summarize
import notify
import news
import state
from datasource import SOURCES


def run():
    print(f"--- Research Desk run (FORCE_ALL={config.FORCE_ALL}) ---")
    prev = state.load_state()
    new_state = dict(prev)
    sent = 0

    for source_key, ticker, name in config.WATCHLIST:
        source = SOURCES.get(source_key)
        if source is None:
            print(f"[main] {ticker}: unknown source '{source_key}' — skipped")
            continue

        df = source.ohlcv(ticker)
        if df is None:
            continue

        ind = indicators.compute_all(df)
        sig = signals.classify(ind)
        label = sig["label"]
        new_state[ticker] = label

        changed = prev.get(ticker) != label
        print(f"{ticker:16} {label:20} (was {prev.get(ticker, '—')})")

        if config.FORCE_ALL or (changed and sig["bias"] != "neutral"):
            headlines = news.fetch_headlines(name)          # only fires on alerts
            summary = summarize.summarize(name, ticker, sig, ind, headlines)
            msg = notify.build_message(name, ticker, sig, ind, summary, headlines)
            if notify.send_telegram(msg):
                sent += 1

    state.save_state(new_state)
    print(f"--- Done. {sent} alert(s) sent. ---")


if __name__ == "__main__":
    run()