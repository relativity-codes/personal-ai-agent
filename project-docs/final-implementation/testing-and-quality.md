# Testing and Quality

## Summary

The project includes backend unit and integration tests, frontend production-build checks, and CI validation for Cloud Run deployment. This document summarizes what reviewers can run and what quality caveats are known in the current implementation.

## Test Folder Structure

```text
backend/
└── tests/
    ├── integration/                   # API and system-level checks
    ├── unit/                          # Isolated logic checks
    └── conftest.py                    # Shared fixtures
frontend/
├── app/                               # Route-level behavior under build
└── lib/                               # Client/chat/auth helpers
.github/
└── workflows/
    └── deploy-cloud-run.yml           # CI test + container build checks
```

## Backend Tests

Backend tests live in `backend/tests`.

Test groups include:

- Health and application startup checks.
- Authentication dependency checks.
- User API integration checks.
- MCP registry, schema, and invoke checks.
- Cache service checks.
- Security claim and validator checks.
- Notion and integration normalization checks.

Useful command:

```bash
cd backend
uv sync --all-groups
uv run pytest
```

Focused health check used during recent implementation:

```bash
cd backend
uv run pytest tests/integration/test_health.py -q
```

Expected current behavior: the focused health check passes. Pydantic deprecation warnings are emitted for class-based model config in some schemas.

## Frontend Build Check

The frontend is statically exported, so the production build is the most important reviewer check.

```bash
cd frontend
npm run build
```

Expected current behavior: the build completes and writes static output to `frontend/out`. A React hook dependency warning may be emitted for `useAuth`.

## Workflow Checks

The GitHub Actions workflow in [`../../.github/workflows/deploy-cloud-run.yml`](../../.github/workflows/deploy-cloud-run.yml) performs:

- Backend health test.
- Docker build verification.
- Image push to Artifact Registry for deploy events.
- Cloud Run deployment with generated environment file.

The workflow YAML was parsed successfully during implementation. A full local Docker build was attempted, but local Docker was unavailable because the Docker daemon was not running.

## Known Implementation Caveats

### Frontend API Credentials Option

`apiFetch` currently sets `"credentials": "include"` inside request headers. Browser `fetch` expects `credentials: "include"` as a top-level option. Same-origin Cloud Run deployment reduces the impact, but this should be fixed for cross-origin deployment.

### Frontend User Hook

`useAuth` currently treats `apiFetch('/api/v1/users/me')` as a raw user object. `apiFetch` returns an `ApiResult<T>` wrapper. The hook should unwrap `data` before storing the user.

### WebSocket Chat Path

Cloud Run supports WebSockets, but the WebSocket endpoint should be tested end-to-end after deployment because long-lived connections depend on Cloud Run timeout settings and client reconnection behavior.

### MCP Implementation Split

The active runtime registry is `app/mcp_alt`. A legacy `app/mcp` implementation remains in the repository and is still referenced by some tests or historical paths. Reviewers should evaluate `mcp_alt` as the current runtime layer.

### Secrets Hygiene

Environment examples and docs should only contain placeholders. If any real token-like values are found in `.env.example` or historical docs, rotate those credentials and replace them with placeholders before public submission.

## Folded Tool Contract Note

The old `tool-bug-fix.md` content has been folded into this documentation set. The relevant current implementation lives in the action agent:

- Tool schemas are cached by `MCPAltRegistry.initialize()`.
- Planner/action logic can inspect the tool catalog.
- The action agent validates arguments against tool schemas before invocation.
- Placeholder substitution resolves user context and prior task outputs.
- Result serialization/parsing makes MCP tool outputs safer for downstream LLM summarization.

This behavior is documented in [`agent-workflow.md`](agent-workflow.md) and [`integrations-and-mcp.md`](integrations-and-mcp.md).

## Reviewer Checklist

1. Read [`overview.md`](overview.md) for the full current implementation summary.
2. Run the backend focused health test.
3. Run the frontend production build.
4. Review [`deployment.md`](deployment.md) for Cloud Run, CockroachDB, Redis Cloud, and GitHub Actions setup.
5. Confirm provider credentials are placeholders in committed docs and examples.

