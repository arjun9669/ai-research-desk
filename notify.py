"""Telegram notification formatting and delivery with safe escaping."""
from html import escape

import requests
import config

_EMOJI = {"bullish": "🟢", "bearish": "🔴", "neutral": "⚪"}


def build_message(name, ticker, sig, ind, summary, headlines=None) -> str:
    # Headline and LLM text are untrusted external inputs; escape Telegram HTML.
    emoji = _EMOJI.get(sig["bias"], "⚪")
    lines = [
        f"{emoji} <b>{escape(str(name))}</b> (<code>{escape(str(ticker))}</code>)",
        f"<b>Signal:</b> {escape(sig['bias'].title())} — {escape(str(sig['reason']))}",
        f"<b>Readings:</b> Price {escape(str(ind.get('price')))} · RSI {escape(str(ind.get('rsi')))}",
        "",
        escape(str(summary)),
    ]
    if headlines:
        lines += ["", "<b>Recent news:</b>"]
        lines += [
            f"• {escape(str(h.get('title', '')))} <i>({escape(str(h.get('source', '')))})</i>"
            for h in headlines[:3]
        ]
    return "\n".join(lines)


def send_telegram(text: str) -> bool:
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        print("[notify] Telegram credentials not configured; delivery failed")
        return False
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={
            "chat_id": config.TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }, timeout=20)
        if response.status_code != 200 or not response.json().get("ok", False):
            print(f"[notify] Telegram delivery rejected (HTTP {response.status_code})")
            return False
        return True
    except (requests.RequestException, ValueError) as exc:
        # Exception messages can include the Telegram API URL (and bot token).
        print(f"[notify] Telegram delivery failed: {type(exc).__name__}")
        return False
