#!/usr/bin/env python3
"""
Batch eval harness: HTTP calls to the running backend + optional OpenRouter LLM-as-judge.

This module is intentionally standalone — it does NOT import application code under
`backend/app`. Install deps: `pip install -r scripts/eval/requirements-eval.txt`
(or use the backend venv which already includes httpx).

Example:
  export EVAL_BASE_URL=http://127.0.0.1:8000
  export OPENROUTER_API_KEY=sk-or-...
  python3 scripts/eval/run_batch.py \\
    --cases scripts/eval/fixtures/eval_cases.jsonl \\
    --out scripts/eval/runs/latest.jsonl
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import time
from pathlib import Path
from typing import Any

import httpx

DEFAULT_JUDGE_MODEL = "anthropic/claude-3.5-haiku"
OPENROUTER_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {e}") from e
    return rows


def _extract_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if m:
        text = m.group(1).strip()
    return json.loads(text)


async def _call_chat(
    client: httpx.AsyncClient,
    base: str,
    message: str,
    session_id: str | None,
    auth_header: str | None,
) -> tuple[int, dict[str, Any] | str, float]:
    headers: dict[str, str] = {}
    if auth_header:
        headers["Authorization"] = auth_header
    payload: dict[str, Any] = {"message": message}
    if session_id:
        payload["session_id"] = session_id
    t0 = time.perf_counter()
    r = await client.post(f"{base.rstrip('/')}/api/v1/chat/", json=payload, headers=headers)
    elapsed = time.perf_counter() - t0
    try:
        body: dict[str, Any] | str = r.json()
    except Exception:
        body = r.text
    return r.status_code, body, elapsed


async def _fetch_plans(
    client: httpx.AsyncClient,
    base: str,
    auth_header: str | None,
    limit: int,
) -> tuple[int, Any]:
    headers: dict[str, str] = {}
    if auth_header:
        headers["Authorization"] = auth_header
    r = await client.get(
        f"{base.rstrip('/')}/api/v1/plans/",
        params={"skip": 0, "limit": limit},
        headers=headers,
    )
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, r.text


async def _call_judge(
    client: httpx.AsyncClient,
    api_key: str,
    model: str,
    case: dict[str, Any],
    api_status: int,
    api_body: Any,
    plans_snapshot: Any,
) -> dict[str, Any]:
    user_block = {
        "case_id": case.get("case_id"),
        "user_message": case.get("message"),
        "golden_plan": case.get("golden_plan"),
        "golden_final_response": case.get("golden_final_response"),
        "judge_instructions": case.get("judge_instructions"),
        "http_status": api_status,
        "api_response": api_body,
        "plans_snapshot": plans_snapshot,
    }
    system = (
        "You are an evaluation judge for a personal AI agent. Compare the API response "
        "to the golden reference and rubric. Output ONLY a single JSON object with keys: "
        '"pass" (boolean), "scores" (object with integer 1-5 for "correctness", '
        '"tool_alignment", "clarity"), "rationale" (string, max 200 words).'
    )
    payload = {
        "model": model,
        "temperature": 0.1,
        "max_tokens": 800,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user_block, ensure_ascii=False)},
        ],
    }
    r = await client.post(
        f"{OPENROUTER_URL}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=120.0,
    )
    r.raise_for_status()
    data = r.json()
    content = data["choices"][0]["message"]["content"]
    try:
        return _extract_json_object(content)
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        return {"pass": False, "scores": {}, "rationale": f"judge_parse_error: {e}", "raw": content}


async def _run_one(
    sem: asyncio.Semaphore,
    client: httpx.AsyncClient,
    base: str,
    case: dict[str, Any],
    auth_header: str | None,
    fetch_plans: bool,
    judge: bool,
    judge_key: str | None,
    judge_model: str,
) -> dict[str, Any]:
    async with sem:
        sid = case.get("session_id")
        session_str = str(sid) if sid else None
        status, body, elapsed = await _call_chat(
            client, base, str(case["message"]), session_str, auth_header
        )
        plans_snapshot: Any | None = None
        if fetch_plans and status == 200:
            ps, pj = await _fetch_plans(client, base, auth_header, limit=30)
            plans_snapshot = {"http_status": ps, "body": pj}
        judge_result: dict[str, Any] | None = None
        if judge and judge_key:
            try:
                judge_result = await _call_judge(
                    client, judge_key, judge_model, case, status, body, plans_snapshot
                )
            except Exception as e:
                judge_result = {"pass": False, "scores": {}, "rationale": f"judge_error: {e!s}"}
        return {
            "case_id": case.get("case_id"),
            "http_status": status,
            "latency_seconds": round(elapsed, 3),
            "api_response": body,
            "plans_snapshot": plans_snapshot,
            "judge": judge_result,
        }


async def _async_main(args: argparse.Namespace) -> None:
    base = args.base_url or os.environ.get("EVAL_BASE_URL", "http://127.0.0.1:8000")
    auth_header = args.auth_header or os.environ.get("EVAL_AUTH_HEADER")
    judge_key = None if args.no_judge else (args.openrouter_key or os.environ.get("OPENROUTER_API_KEY"))
    if not args.no_judge and not judge_key:
        raise SystemExit("Set OPENROUTER_API_KEY or pass --openrouter-key, or use --no-judge")

    cases_path = Path(args.cases)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cases = _load_jsonl(cases_path)
    if args.max_cases is not None:
        cases = cases[: int(args.max_cases)]

    sem = asyncio.Semaphore(max(1, int(args.concurrency)))
    timeout = httpx.Timeout(args.timeout, connect=30.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        tasks = [
            _run_one(
                sem,
                client,
                base,
                c,
                auth_header,
                not args.no_plans,
                not args.no_judge,
                judge_key,
                args.judge_model,
            )
            for c in cases
        ]
        results = await asyncio.gather(*tasks)

    with out_path.open("w", encoding="utf-8") as out:
        for case, result in zip(cases, results):
            row = {**{k: v for k, v in case.items()}, **result}
            out.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Wrote {len(results)} rows to {out_path}")


def main() -> None:
    p = argparse.ArgumentParser(description="Batch HTTP eval + optional LLM judge (standalone).")
    p.add_argument("--cases", default="scripts/eval/fixtures/eval_cases.jsonl", help="Input JSONL path")
    p.add_argument("--out", default="scripts/eval/runs/latest.jsonl", help="Output JSONL path")
    p.add_argument("--base-url", default=None, help="Override EVAL_BASE_URL")
    p.add_argument("--auth-header", default=None, help="Raw Authorization header value, e.g. 'Bearer …'")
    p.add_argument("--concurrency", type=int, default=2)
    p.add_argument("--max-cases", type=int, default=None)
    p.add_argument("--timeout", type=float, default=180.0, help="Per-request timeout (seconds)")
    p.add_argument("--no-plans", action="store_true", help="Skip GET /api/v1/plans/ after each chat")
    p.add_argument("--no-judge", action="store_true", help="Skip OpenRouter judge calls")
    p.add_argument("--openrouter-key", default=None, help="Override OPENROUTER_API_KEY")
    p.add_argument("--judge-model", default=os.environ.get("EVAL_JUDGE_MODEL", DEFAULT_JUDGE_MODEL))
    args = p.parse_args()
    asyncio.run(_async_main(args))


if __name__ == "__main__":
    main()
