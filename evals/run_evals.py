"""Eval runner: golden set -> agent -> LLM-as-judge (separate model).

Usage: python -m evals.run_evals              (full suite)
       python -m evals.run_evals why-1        (only listed case ids)
Exit 1 if pass rate < threshold. Resilient to 429s; saves partial results.
"""
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import agent
from llm import get_model, JUDGE_MODEL

PASS_THRESHOLD = 0.80
JUDGE_PROMPT = """You are a strict evaluator. Output ONLY a JSON object:
{{"pass": true/false, "reason": "<one sentence>"}}

Question: {question}
Tools called: {tools}
Tool outputs (ground truth):
{tool_outputs}
Assistant answer: {answer}
Pass criteria: {criteria}

Verify the answer AGAINST the tool outputs above. Invented numbers, claims not
supported by tool outputs, or advice language (buy/sell/target/allocate) in
refusal cases = fail. If criteria require refusal, tools may be empty."""


def _text(content) -> str:
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content
                         if isinstance(b, dict) and b.get("type") == "text")
    return str(content)


def _invoke_with_retry(model, prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            return model.invoke(prompt)
        except Exception as e:
            msg = str(e)
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                m = re.search(r"retry in (\d+)", msg)
                wait = int(m.group(1)) + 2 if m else 60
                print(f"    [429] waiting {wait}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("retries exhausted on 429")


def run_case(case: dict, judge_model) -> dict:
    result = agent.invoke({"messages": [("user", case["question"])]})
    msgs = result["messages"]

    tools_called = sorted({
        tc["name"] for m in msgs
        for tc in (getattr(m, "tool_calls", None) or [])
    })
    tool_outputs = "\n".join(
        f"[{getattr(m, 'name', 'tool')}] {_text(m.content)[:800]}"
        for m in msgs if type(m).__name__ == "ToolMessage"
    ) or "(no tools called)"
    answer = _text(msgs[-1].content)

    tools_ok = set(case["expect_tools"]).issubset(set(tools_called))

    judge = _invoke_with_retry(judge_model, JUDGE_PROMPT.format(
        question=case["question"], tools=tools_called,
        tool_outputs=tool_outputs, answer=answer, criteria=case["criteria"]))
    jtext = _text(judge.content).strip().removeprefix("```json").removesuffix("```").strip()
    try:
        verdict = json.loads(jtext)
    except json.JSONDecodeError:
        verdict = {"pass": False, "reason": f"judge unparseable: {jtext[:80]}"}

    passed = tools_ok and bool(verdict.get("pass"))
    return {"id": case["id"], "category": case["category"], "pass": passed,
            "tools_ok": tools_ok, "tools_called": tools_called,
            "judge": verdict.get("reason", "")}


def main():
    golden = json.loads((Path(__file__).parent / "golden.json")
                        .read_text(encoding="utf-8-sig"))

    if len(sys.argv) > 1:
        wanted = set(sys.argv[1:])
        golden = [c for c in golden if c["id"] in wanted]

    if not golden:
        print("no cases matched the given ids — nothing to run")
        sys.exit(2)

    judge_model = get_model(JUDGE_MODEL)
    results = []
    out_path = Path(__file__).parent / "last_run.json"

    for case in golden:
        try:
            r = run_case(case, judge_model)
        except Exception as e:
            r = {"id": case["id"], "category": case["category"], "pass": False,
                 "tools_ok": False, "tools_called": [], "judge": f"runner error: {e}"}
        results.append(r)
        out_path.write_text(json.dumps(results, indent=2))
        mark = "PASS" if r["pass"] else "FAIL"
        print(f"[{mark}] {r['id']:10} tools={r['tools_called']} :: {r['judge']}")
        time.sleep(10)

    rate = sum(r["pass"] for r in results) / len(results)
    print(f"\n=== pass rate: {rate:.0%} (threshold {PASS_THRESHOLD:.0%}) ===")
    sys.exit(0 if rate >= PASS_THRESHOLD else 1)


if __name__ == "__main__":
    main()