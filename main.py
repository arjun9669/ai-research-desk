"""AI Market Research Desk — scheduled market-data and alert pipeline.

Alert state means the last successfully delivered signal, not the last observed
signal. Failed deliveries must remain eligible for retry on the next run.
"""
import datetime

import config
import indicators
import news
import notify
import signals
import state
import summarize
from datasource import SOURCES


def run():
    print(f"--- Research Desk run (FORCE_ALL={config.FORCE_ALL}) ---")
    prev = state.load_state()
    new_state = dict(prev)
    sent = 0
    failures = []

    for source_key, ticker, name in config.WATCHLIST:
        try:
            source = SOURCES.get(source_key)
            if source is None:
                raise ValueError(f"unknown source type: {source_key}")
            df = source.ohlcv(ticker)
            if df is None or df.empty:
                raise ValueError("no usable price history")
            ind = indicators.compute_all(df)
            sig = signals.classify(ind)
            label = sig["label"]
            changed = prev.get(ticker) != label
            print(f"{ticker:16} {label:20} (was {prev.get(ticker, '—')})")

            should_alert = config.FORCE_ALL or (changed and sig["bias"] != "neutral")
            if should_alert:
                headlines = news.fetch_headlines(name)
                summary = summarize.summarize(name, ticker, sig, ind, headlines)
                message = notify.build_message(name, ticker, sig, ind, summary, headlines)
                if not notify.send_telegram(message):
                    raise RuntimeError("notification not delivered; state retained for retry")
                sent += 1

            # No alert required or successful delivery: safe to advance state.
            new_state[ticker] = label
        except Exception as exc:
            # Preserve last delivered state for this ticker, so alert attempts retry.
            failures.append(ticker)
            print(f"[main] {ticker}: {type(exc).__name__}: {exc}")

    # Save valid progress even when individual tickers fail.
    state.save_state(new_state)

    if sent == 0 and not failures and datetime.datetime.now().weekday() == 4:
        if not notify.send_telegram(
            "✅ <b>Desk heartbeat</b> — no signal changes requiring alerts."
        ):
            failures.append("weekly-heartbeat")

    print(f"--- Done. {sent} delivered alert(s); {len(failures)} failure(s). ---")
    if failures:
        raise RuntimeError(f"Research Desk had failed tickers: {', '.join(failures)}")


if __name__ == "__main__":
    run()
