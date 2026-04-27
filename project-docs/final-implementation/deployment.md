# Deployment

## Summary

The current production deployment path is Google Cloud Run with one service. The service runs FastAPI and serves the exported Next.js frontend from the same container.

## Deployment Folder Structure

```text
personal-ai-agent/
├── Dockerfile                         # Multi-stage build: frontend + backend
├── .dockerignore                      # Build context exclusions
├── .github/
│   └── workflows/
│       └── deploy-cloud-run.yml       # Test, build, push, deploy pipeline
├── backend/
│   ├── README.md                      # Backend/deploy operational notes
│   ├── app/                           # FastAPI runtime code
│   └── alembic/                       # DB migrations
└── frontend/
    ├── next.config.mjs                # Static export settings
    └── package.json
```

## Chosen Deployment Model

The project uses the single-service Cloud Run option:

```mermaid
flowchart TD
gha["GitHub Actions"] --> artifact["Artifact Registry image"]
artifact --> cloudRun["Cloud Run service"]
cloudRun --> fastapi["FastAPI API and WebSocket routes"]
cloudRun --> staticApp["Exported Next.js static app"]
fastapi --> cockroach["CockroachDB"]
fastapi --> redisCloud["Redis Cloud"]
userBrowser["User browser"] --> customDomain["Custom domain mapping"]
customDomain --> cloudRun
```

This keeps browser requests same-origin:

- Frontend pages are served by FastAPI from `static/`.
- REST API calls use `/api/v1/...`.
- WebSocket chat uses `/ws/chat`.

## Docker Image

The root Dockerfile is multi-stage:

1. `node:20-slim` installs frontend dependencies and runs `npm run build`.
2. `python:3.11-slim` installs `uv` and backend dependencies with `uv sync --frozen --no-dev --no-install-project`.
3. Backend code, Alembic files, system prompts, and exported frontend assets are copied into `/app`.
4. The container starts uvicorn on Cloud Run's `PORT`, defaulting to `8080`.

The image command is:

```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
```

## GitHub Actions

The workflow in [`../../.github/workflows/deploy-cloud-run.yml`](../../.github/workflows/deploy-cloud-run.yml) has three jobs:

- `backend-tests`: installs backend dependencies and runs the health integration test.
- `container-build`: verifies the Docker build on pull requests and pushes.
- `deploy`: authenticates to Google Cloud, builds and pushes the image to Artifact Registry, generates a Cloud Run env file, and deploys the service.

Deployment is skipped for pull requests and runs for `main` pushes or manual workflow dispatch.

Google Cloud authentication uses Workload Identity Federation rather than a long-lived JSON key.

## Runtime Services

### Database

The current database target is CockroachDB. The backend supports:

- `DATABASE_URL`, preferred for hosted CockroachDB.
- Individual `POSTGRES_*` values for Postgres-compatible configuration.

Migrations should be run from a controlled environment such as a one-off admin command or a gated GitHub Actions job. They should not run automatically on every container start.

### Redis

The current cache target is Redis Cloud. Use `REDIS_URL`, preferably with `rediss://` when TLS is required by the provider.

### Domain

The deployment assumes Cloud Run domain mapping. After mapping the custom domain, set:

- `HOST`
- `CORS_ORIGINS`
- `ALLOWED_HOSTS`

These should point to the deployed custom domain and any explicitly allowed local/test origins.

## GitHub Variables and Secrets

Repository variables are used for non-secret deployment and provider identifiers:

- `GCP_PROJECT_ID`
- `GCP_REGION`
- `GAR_REPOSITORY`
- `CLOUD_RUN_SERVICE`
- `GCP_WORKLOAD_IDENTITY_PROVIDER`
- `GCP_SERVICE_ACCOUNT`
- `HOST`
- `CORS_ORIGINS`
- `ALLOWED_HOSTS`
- `NEXT_PUBLIC_GOOGLE_CLIENT_ID`
- `GITHUB_CLIENT_ID`
- `NOTION_CLIENT_ID`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_OAUTH_SCOPES`
- `OPENROUTER_BASE_URL`
- `OPENROUTER_DEFAULT_MODEL`
- `OPENROUTER_FALLBACK_MODELS`

Repository secrets are used for runtime credentials:

- `DATABASE_URL`, or individual `POSTGRES_*` secrets.
- `REDIS_URL`
- `SECRET_KEY`
- `GITHUB_CLIENT_SECRET`
- `GITHUB_TOKEN`
- `NOTION_CLIENT_SECRET`
- `NOTION_TOKEN`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REFRESH_TOKEN`
- `GOOGLE_CALENDAR_ACCESS_TOKEN`
- `GMAIL_ACCESS_TOKEN`
- `OPENROUTER_API_KEY`

Do not commit real tokens or private keys to `.env.example`, docs, or workflow files.

## Manual Deployment Shape

GitHub Actions automates deployment, but the equivalent manual shape is:

```bash
docker build -t REGION-docker.pkg.dev/PROJECT/REPOSITORY/SERVICE:latest .
docker push REGION-docker.pkg.dev/PROJECT/REPOSITORY/SERVICE:latest
gcloud run deploy SERVICE \
  --image REGION-docker.pkg.dev/PROJECT/REPOSITORY/SERVICE:latest \
  --region REGION \
  --allow-unauthenticated \
  --port 8080
```

## Deployment Caveats

- Cloud Run supports WebSockets, but request timeout and client reconnection behavior should be reviewed for long-running sessions.
- CockroachDB and Redis Cloud must allow network access from Cloud Run. If strict IP allowlisting is enabled, a stable egress pattern may be needed.
- The Docker daemon was not running during the last local verification, so the Docker build was not validated locally; the GitHub Actions runner is expected to perform that check.
- Static export means the frontend cannot depend on Next.js server runtime behavior in production.

