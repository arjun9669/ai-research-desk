"""Output guardrails: block advice language before it reaches the user.

Layer 1 (deterministic, free): regex policy check.
Layer 2 (LLM judge): lives in the eval suite, not runtime.
"""
import re

_ADVICE_PATTERNS = [
    r"\byou should (buy|sell|invest|enter|exit)\b",
    r"\bI (recommend|suggest|advise) (buying|selling|investing)\b",
    r"\b(buy|sell) (now|today|tomorrow|immediately)\b",
    r"\bprice target\b.*\b\d",
    r"\btarget (of|price)\s*(AED|USD|\$)?\s*\d",
    r"\ballocate \d+\s*%\b",
    r"\b\d+\s*% of (your|the) (savings|portfolio|capital)\b",
]
_COMPILED = [re.compile(p, re.IGNORECASE) for p in _ADVICE_PATTERNS]
DISCLAIMER = "Informational only — not financial advice."


def check(text: str) -> dict:
    """Returns {'ok': bool, 'violations': [pattern, ...]}."""
    hits = [p.pattern for p in _COMPILED if p.search(text)]
    return {"ok": not hits, "violations": hits}


def enforce(text: str) -> str:
    """Blocks violating output; guarantees disclaimer on clean output."""
    result = check(text)
    if not result["ok"]:
        return ("I can describe signals and data, but I can't provide "
                f"investment advice or price targets. {DISCLAIMER}")
    if DISCLAIMER.rstrip(".").lower() not in text.lower():
        return f"{text}\n\n{DISCLAIMER}"
    return text
