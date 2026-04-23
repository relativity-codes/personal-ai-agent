# Batch evaluation fixtures

This folder holds **JSONL** golden cases for API-driven evaluation (no UI). Each line is one JSON object.

## Branch

Work on branch **`eval`**, cut from **`develop`**. If your local `develop` is behind `origin/develop`, run:

```bash
git checkout develop && git pull origin develop
git checkout eval
git merge develop
```

## Fixture file

- **[fixtures/eval_cases.jsonl](fixtures/eval_cases.jsonl)** — 20 use cases aligned with the product: multi-tool standup prep, GitHub PR/issue flows, Notion pages and database queries, Google Calendar availability and blocking, Gmail digests and drafts, cross-tool briefings, and a low-confidence clarification case.

### Schema (per line)

| Field | Description |
|--------|-------------|
| `case_id` | Stable id (`eval-001` … `eval-020`). |
| `message` | User utterance sent to `POST /api/v1/chat/`. |
| `session_id` | `null` or a UUID string to continue a thread. |
| `golden_plan` | Reference plan: `intent_type` plus `tasks[]` with `step`, `description`, `mcp_server`, `tool` for judge comparison (not enforced by the API). |
| `golden_final_response` | Reference assistant reply text for LLM-as-judge. |
| `judge_instructions` | Rubric hints for scoring. |

## Editing cases

Edit [fixtures/eval_cases.jsonl](fixtures/eval_cases.jsonl) directly—one JSON object per line (valid JSONL).

## Next steps

- Point the batch harness at `fixtures/eval_cases.jsonl` and a **disposable Postgres** `POSTGRES_DB` (see project docs).
- Run the API with `DEV_AUTH_BYPASS=true` for unattended HTTP calls unless you supply real Clerk JWTs.
