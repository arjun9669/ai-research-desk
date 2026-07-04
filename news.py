"""Signal-triggered news retrieval: Google News RSS, stdlib-only."""
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

UA = {"User-Agent": "Mozilla/5.0 (research-desk)"}


def fetch_headlines(query: str, limit: int = 5) -> list[dict]:
    """Top recent headlines for a query. Returns [{'title','source','age_h'}]."""
    url = (
        "https://news.google.com/rss/search"
        f"?q={requests.utils.quote(query)}&hl=en-AE&gl=AE&ceid=AE:en"
    )
    try:
        r = requests.get(url, headers=UA, timeout=15)
        r.raise_for_status()
        root = ET.fromstring(r.content)
    except Exception as e:
        print(f"[news] '{query}': {e}")
        return []

    now = datetime.now(timezone.utc)
    items = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        pub = item.findtext("pubDate")
        if not title:
            continue
        try:
            age_h = (now - parsedate_to_datetime(pub)).total_seconds() / 3600
        except Exception:
            age_h = 999.0
        # Google News appends " - Source" to titles; split it out
        source = ""
        m = re.match(r"^(.*)\s+-\s+([^-]+)$", title)
        if m:
            title, source = m.group(1).strip(), m.group(2).strip()
        items.append({"title": title, "source": source, "age_h": age_h})

    # Relevance = recency-weighted keyword overlap with the query
    q_words = {w.lower() for w in query.split() if len(w) > 2}

    def score(it):
        overlap = sum(1 for w in q_words if w in it["title"].lower())
        recency = max(0.0, 1.0 - it["age_h"] / 168)  # decays over 7 days
        return overlap * 2 + recency

    items.sort(key=score, reverse=True)
    fresh = [it for it in items if it["age_h"] < 168]  # last 7 days only
    return (fresh or items)[:limit]