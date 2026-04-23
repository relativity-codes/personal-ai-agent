# Batch evaluation (standalone)

Eval code here is **independent of the FastAPI app**: it only uses **HTTP** (`httpx`) to talk to a **running** backend and optionally **OpenRouter** for LLM-as-judge. It does **not** import `backend/app` so you can merge or run eval without coupling to internal modules.

## Layout

| Path | Purpose |
|------|---------|
| [fixtures/eval_cases.jsonl](fixtures/eval_cases.jsonl) | Golden cases (one JSON object per line). |
| [run_batch.py](run_batch.py) | Async batch runner: `POST /api/v1/chat/`, optional `GET /api/v1/plans/`, optional judge. |
| [requirements-eval.txt](requirements-eval.txt) | Minimal `httpx` pin for a small venv. |
| [.env.eval.example](.env.eval.example) | Environment template (copy to `.env.eval`, do not commit secrets). |
| [runs/](runs/) | Default output directory (gitignored contents except `.gitignore`; avoids root `out/` ignore rule). |

## Branch workflow

Work on branch **`eval`** (or merge from `develop` as needed). See git history for fixture commits.

## Install (eval-only venv)

From repo root:

```bash
python3 -m venv .venv-eval
source .venv-eval/bin/activate
pip install -r scripts/eval/requirements-eval.txt
```

Alternatively use the **backend** virtualenv (it already depends on `httpx`):

```bash
cd backend && source .venv/bin/activate
cd ..   # repo root
python3 scripts/eval/run_batch.py --help
```

## Configure

1. Start the API (separate terminal), e.g. `DEV_AUTH_BYPASS=true` for unattended runs.
2. Copy env template: `cp scripts/eval/.env.eval.example scripts/eval/.env.eval` and fill keys.
3. Export or source: `set -a && source scripts/eval/.env.eval && set +a`

## Run

```bash
export EVAL_BASE_URL=http://127.0.0.1:8000
export OPENROUTER_API_KEY=sk-or-...
python3 scripts/eval/run_batch.py \
  --cases scripts/eval/fixtures/eval_cases.jsonl \
  --out scripts/eval/runs/run.jsonl \
  --concurrency 2
```

Useful flags:

- `--no-judge` — only hit the API (no OpenRouter spend).
- `--no-plans` — skip `GET /api/v1/plans/` snapshot after each chat.
- `--max-cases 3` — smoke subset.
- `--auth-header 'Bearer …'` — when not using dev bypass.

## Output format

Each line in the output JSONL merges the input case with:

- `http_status`, `latency_seconds`, `api_response`
- `plans_snapshot` (optional)
- `judge` — parsed JSON from the judge model (`pass`, `scores`, `rationale`) or an error object

## Integration note

The harness assumes the backend exposes **`POST /api/v1/chat/`** and **`GET /api/v1/plans/`** as in production. Fixing auth or repository wiring inside `backend/app` is **separate** from this folder; keep app changes in normal feature PRs.

## Fixture schema

| Field | Description |
|--------|-------------|
| `case_id` | Stable id. |
| `message` | User message for chat. |
| `session_id` | `null` or UUID string. |
| `golden_plan` | Reference plan for the judge. |
| `golden_final_response` | Reference assistant text. |
| `judge_instructions` | Rubric for scoring. |

Edit [fixtures/eval_cases.jsonl](fixtures/eval_cases.jsonl) directly (valid JSONL: one JSON object per line).
