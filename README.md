# AI Market Research Desk

Monitors selected DFM stocks daily, detects technical signals (RSI / MACD / moving-average crossovers),
writes a plain-English summary, and sends an alert to Telegram. Research aid — **not** financial advice,
**not** auto-trading.

## Architecture
```
data.py        → pull daily prices (yfinance, free)
indicators.py  → RSI, MACD, SMA (pure pandas, no fragile deps)
signals.py     → one discrete signal label per stock
state.py       → remembers last signal (alert only on change)
summarize.py   → Claude turns numbers into a plain sentence (descriptive only)
notify.py      → sends to Telegram
main.py        → runs the whole pipeline
```

## Local setup (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1     # if blocked: Set-ExecutionPolicy -Scope Process RemoteSigned
pip install -r requirements.txt
copy .env.example .env           # then edit .env with your tokens
```

## Run
```powershell
# First demo — alert on every stock so you see output immediately:
$env:FORCE_ALL="true"; python main.py

# Normal mode — alert only when a signal changes:
python main.py
```

## Secrets needed
| Variable | Where to get it |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Create a bot via @BotFather in Telegram |
| `TELEGRAM_CHAT_ID`   | Message your bot, then open `https://api.telegram.org/bot<TOKEN>/getUpdates` and read `chat.id` |
| `ANTHROPIC_API_KEY`  | console.anthropic.com (optional — without it, summaries use a template) |

## Automation
`.github/workflows/desk.yml` runs the desk every weekday at 15:30 Gulf time via GitHub Actions.
Add the three secrets under repo **Settings → Secrets and variables → Actions**. The workflow
commits `state.json` back to the repo so it remembers signals between runs.
