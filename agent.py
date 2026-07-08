"""Research Desk agent — conversational analysis over the pipeline.

Usage:  python agent.py "why did DIB move this week?"
        python agent.py            (interactive REPL)
"""
import sys
from langchain.agents import create_agent
from llm import get_model
from agent_tools import TOOLS
import guardrails

SYSTEM = (
    "You are the Research Desk agent for a UAE equities + crypto watchlist. "
    "Answer by CALLING TOOLS — never guess prices, indicators, or news. "
    "Typical flow: run_screen to see what moved → get_quote for specifics → "
    "fetch_news with a query YOU compose; if results look thin or off-topic, "
    "re-query with refined terms before answering. "
    "Rules: descriptive analysis only — never advise buying/selling, never "
    "give price targets. End every answer with: "
    "'Informational only — not financial advice.'"
)

agent = create_agent(get_model(), TOOLS, system_prompt=SYSTEM)


def ask(question: str) -> str:
    result = agent.invoke({"messages": [("user", question)]})
    content = result["messages"][-1].content
    if isinstance(content, list):
        content = "\n".join(
            b.get("text", "") for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        )
    return guardrails.enforce(content)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(ask(" ".join(sys.argv[1:])))
    else:
        print("Research Desk agent — Ctrl+C to exit")
        while True:
            q = input("\nask> ").strip()
            if q:
                print(ask(q))