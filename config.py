"""Central configuration. Edit the watchlist and thresholds here — nothing else needs touching."""
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv only needed locally; GitHub uses Actions secrets 

# --- Watchlist: DFM tickers verified on Yahoo Finance (.AE suffix) ---
# Add/remove freely. Format: "TICKER": "Display name"
WATCHLIST = [
    # (source,   symbol,            display name)
    ("equity", "EMAAR.AE",        "Emaar Properties"),
    ("equity", "EMIRATESNBD.AE",  "Emirates NBD"),
    ("equity", "DIB.AE",          "Dubai Islamic Bank"),
    ("equity", "SALIK.AE",        "Salik"),
    ("equity", "DFM.AE",          "Dubai Financial Market"),
    ("crypto", "BTC/USDT",        "Bitcoin"),
    ("crypto", "ETH/USDT",        "Ethereum"),
]

# --- Indicator settings (standard defaults) ---
RSI_PERIOD       = 14
RSI_OVERSOLD     = 30      # below this = oversold (bullish lean)
RSI_OVERBOUGHT   = 70      # above this = overbought (bearish lean)
MACD_FAST        = 12
MACD_SLOW        = 26
MACD_SIGNAL      = 9
SMA_SHORT        = 50
SMA_LONG         = 200
HISTORY_PERIOD   = "2y"    # enough bars for the 200-day average + crossover

# --- Behaviour ---
# When True, sends an alert for every stock on every run (use for the first demo).
# When False, sends ONLY when a stock's signal changes vs. the last run (normal mode).
FORCE_ALL = os.getenv("FORCE_ALL", "false").lower() == "true"

STATE_FILE = "state.json"

# --- Secrets (read from environment / GitHub Actions secrets) ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")
ANTHROPIC_API_KEY  = os.getenv("ANTHROPIC_API_KEY", "")

# Cheap, fast model for short summaries
CLAUDE_MODEL = "claude-haiku-4-5-20251001"
