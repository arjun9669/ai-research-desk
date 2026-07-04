SYSTEM_PROMPT = (
    "You are a market research assistant. Given a stock's technical signal and "
    "recent headlines, write 1-2 plain-English sentences: what the indicators "
    "show, and IF the headlines plausibly relate, the likely context. Rules: "
    "describe only — never advise buying/selling, no price targets. If headlines "
    "seem unrelated, ignore them rather than forcing a connection. Output only "
    "the sentences."
)


def summarize(name: str, ticker: str, sig: dict, ind: dict,
              headlines: list[dict] | None = None) -> str:
    disclaimer = "Informational only — not financial advice."
    if not config.ANTHROPIC_API_KEY:
        return _fallback(name, sig, ind)
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        news_block = "\n".join(
            f"- {h['title']} ({h['source']}, {h['age_h']:.0f}h ago)"
            for h in (headlines or [])
        ) or "None available"
        user_msg = (
            f"Stock: {name} ({ticker})\nPrice: {ind.get('price')}\n"
            f"RSI: {ind.get('rsi')}\nSignal: {sig['reason']} ({sig['bias']})\n"
            f"Recent headlines:\n{news_block}"
        )
        resp = client.messages.create(
            model=config.CLAUDE_MODEL, max_tokens=160,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        text = "".join(b.text for b in resp.content if b.type == "text").strip()
        return f"{text} {disclaimer}" if text else _fallback(name, sig, ind)
    except Exception:
        return _fallback(name, sig, ind)