"""AI layer: turn indicator numbers into a short, plain-English note.

Hard rule baked into the system prompt: DESCRIPTIVE only, never prescriptive.
No "buy/sell at X". Always ends with a disclaimer. If no API key is set, falls
back to a templated sentence so the pipeline still works without Claude.
"""
import config

SYSTEM_PROMPT = (
    "You are a market research assistant. Given a stock and its technical indicator "
    "readings, write ONE short, plain-English sentence describing what the indicators "
    "show. Rules: describe only — never tell the reader to buy, sell, or enter at a "
    "price. No price targets. No advice. Plain language a non-trader understands. "
    "Output only the sentence, no preamble."
)


def _fallback(name: str, sig: dict, ind: dict) -> str:
    return f"{name}: {sig['reason']}. Informational only, not financial advice."


def summarize(name: str, ticker: str, sig: dict, ind: dict) -> str:
    disclaimer = "Informational only — not financial advice."

    if not config.ANTHROPIC_API_KEY:
        return _fallback(name, sig, ind)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        user_msg = (
            f"Stock: {name} ({ticker})\n"
            f"Price: {ind.get('price')}\n"
            f"RSI: {ind.get('rsi')}\n"
            f"MACD: {ind.get('macd')} vs signal {ind.get('macd_signal')}\n"
            f"Detected condition: {sig['reason']} (overall lean: {sig['bias']})"
        )
        resp = client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=120,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        text = "".join(b.text for b in resp.content if b.type == "text").strip()
        return f"{text} {disclaimer}" if text else _fallback(name, sig, ind)
    except Exception as e:
        pass
        return _fallback(name, sig, ind)
