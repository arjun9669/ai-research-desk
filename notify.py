"""Output layer: send the alert to Telegram."""
import requests
import config

BULL = "🟢"
BEAR = "🔴"
FLAT = "⚪"
_EMOJI = {"bullish": BULL, "bearish": BEAR, "neutral": FLAT}


def build_message(name, ticker, sig, ind, summary, headlines=None) -> str:
    emoji = _EMOJI.get(sig["bias"], FLAT)
    lines = [
        f"{emoji} <b>{name}</b>  (<code>{ticker}</code>)",
        f"<b>Signal:</b> {sig['bias'].title()} — {sig['reason']}",
        f"<b>Readings:</b> Price {ind.get('price')} · RSI {ind.get('rsi')}",
        "",
        summary,
    ]
    if headlines:
        lines += ["", "<b>Recent news:</b>"]
        lines += [f"• {h['title']} <i>({h['source']})</i>" for h in headlines[:3]]
    return "\n".join(lines)


def send_telegram(text: str) -> bool:
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        print("[notify] Telegram secrets missing — printing instead:\n" + text + "\n")
        return False
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={
            "chat_id": config.TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }, timeout=20)
        if r.status_code != 200:
            print(f"[notify] Telegram error {r.status_code}: {r.text}")
            return False
        return True
    except requests.RequestException as e:
        print(f"[notify] Telegram request failed: {e}")
        return False
