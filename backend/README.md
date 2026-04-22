# Backend

FastAPI app for the personal AI agent. Run it with [uv](https://docs.astral.sh/uv/).

## Prerequisites

- Python 3.11 or newer (see `.python-version`)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) installed

## One-time setup

From the `backend` directory:

```bash
cd backend
uv sync
cp .env.example .env
```

Edit `.env` as needed. List-style settings (`CORS_ORIGINS`, `ALLOWED_HOSTS`, `OPENROUTER_FALLBACK_MODELS`) use comma-separated values or a JSON array.

To install dev tools (pytest, etc.):

```bash
uv sync --all-groups
```

## Run the API

```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server listens on port **8000** by default.

- Health: `http://localhost:8000/health`
- OpenAPI (Swagger): `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## MCP tool APIs

Authenticated routes (dev bypass uses a stub user when `DEV_AUTH_BYPASS=true`):

- `GET /api/v1/mcp/servers` — registered integrations (GitHub, Notion, Calendar, Gmail) and `configured` flags.
- `GET /api/v1/mcp/tools` — tool catalog per integration (JSON Schema `input_schema` on each tool).
- `POST /api/v1/mcp/invoke` — body `{ "server_id": "github", "tool": "list_open_pull_requests", "arguments": { ... } }`.

Secrets:

- **GitHub:** `GITHUB_TOKEN` (PAT with `repo` or appropriate scopes for the repos you query).
- **Notion:** `NOTION_TOKEN` (integration token; share databases/pages with the integration).
- **Google Calendar & Gmail:** Google’s user APIs do **not** authenticate with client id + secret alone. Those identify your OAuth **client**. You still need a **user grant**, usually stored as **`GOOGLE_REFRESH_TOKEN`** (from OAuth consent with **offline** access). The app calls `https://oauth2.googleapis.com/token` with `client_id`, `client_secret`, and `refresh_token` to obtain a short-lived **access token** before each Calendar/Gmail request. Alternatively you can paste a static **`GOOGLE_CALENDAR_ACCESS_TOKEN`** and/or **`GMAIL_ACCESS_TOKEN`** (they override the minted token for that API only). Consent scopes must include Calendar and/or Gmail as needed (e.g. `https://www.googleapis.com/auth/calendar.readonly`, `https://www.googleapis.com/auth/gmail.readonly`).

Copy-paste catalog: [samples/mcp_invoke_payloads.json](samples/mcp_invoke_payloads.json) — use a value under **`payloads`** as the **entire** JSON body (do not send `name` / `body` wrappers; those are only for documentation grouping).

### Sample `POST /api/v1/mcp/invoke` payloads

The request body must be exactly **`{ "server_id", "tool", "arguments" }`** at the top level (same shape as each entry under `payloads` in the JSON file). In **Swagger UI**, paste that object only, not the whole `mcp_invoke_payloads.json` file.

Replace placeholders (`YOUR_*`, dates) and run with `curl` (omit `-H Authorization` when `DEV_AUTH_BYPASS=true`):

**GitHub — list open pull requests**

```json
{
  "server_id": "github",
  "tool": "list_open_pull_requests",
  "arguments": {
    "owner": "octocat",
    "repo": "Hello-World",
    "state": "open"
  }
}
```

**GitHub — list commits**

```json
{
  "server_id": "github",
  "tool": "list_commits",
  "arguments": {
    "owner": "octocat",
    "repo": "Hello-World",
    "sha": "HEAD",
    "per_page": 10
  }
}
```

**Notion — query database**

```json
{
  "server_id": "notion",
  "tool": "query_database",
  "arguments": {
    "database_id": "YOUR_DATABASE_UUID",
    "page_size": 10
  }
}
```

**Notion — create page (parent must match your workspace schema)**

```json
{
  "server_id": "notion",
  "tool": "create_page",
  "arguments": {
    "parent_id": "YOUR_PARENT_PAGE_UUID",
    "title": "Standup agenda",
    "parent_type": "page_id"
  }
}
```

**Calendar — list events (needs `GOOGLE_CALENDAR_ACCESS_TOKEN`; RFC3339 times)**

```json
{
  "server_id": "calendar",
  "tool": "list_events",
  "arguments": {
    "time_min": "2026-04-22T00:00:00Z",
    "time_max": "2026-04-29T23:59:59Z",
    "max_results": 20
  }
}
```

**Calendar — detect overlaps (no Google token; local helper)**

```json
{
  "server_id": "calendar",
  "tool": "detect_overlaps",
  "arguments": {
    "events": [
      { "summary": "Meeting A", "start": "2026-04-22T14:00:00Z", "end": "2026-04-22T15:00:00Z" },
      { "summary": "Meeting B", "start": "2026-04-22T14:30:00Z", "end": "2026-04-22T15:30:00Z" }
    ]
  }
}
```

**Gmail — list threads (v1.1 stub unless `GMAIL_ACCESS_TOKEN` is wired)**

```json
{
  "server_id": "gmail",
  "tool": "list_threads",
  "arguments": {
    "query": "is:unread",
    "max_results": 10
  }
}
```

**curl example (GitHub PRs)**

```bash
curl -s -X POST http://localhost:8000/api/v1/mcp/invoke \
  -H "Content-Type: application/json" \
  -d '{"server_id":"github","tool":"list_open_pull_requests","arguments":{"owner":"octocat","repo":"Hello-World","state":"open"}}'
```

## Tests

```bash
cd backend
uv sync --all-groups
uv run pytest
```

Tests load **`backend/.env`** (same as the app). **`tests/integration/test_mcp_live_env.py`** calls real GitHub, Notion, and Google Calendar APIs when the matching variables are set; otherwise those cases **`skip`** with a short reason. Optional: `GITHUB_TEST_OWNER`, `GITHUB_TEST_REPO`, `NOTION_TEST_DATABASE_ID` tune live targets. Run only live-marked tests: `uv run pytest -m live`.

## Frontend (Next.js)

The web app lives in `../frontend`. In a separate terminal:

```bash
cd ../frontend
cp .env.example .env.local
yarn install
yarn dev
```

Then open `http://localhost:3000`. Set `NEXT_PUBLIC_API_URL` in `.env.local` if the API is not on `http://localhost:8000`.

## Database migrations (optional)

When you add SQLAlchemy models and Alembic revisions:

```bash
cd backend
uv run alembic upgrade head
```
