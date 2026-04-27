# Backend

This directory contains the FastAPI application that serves as the backend for the Personal AI Agent.

## Prerequisites

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (a fast Python package installer and resolver)

## Getting Started

Follow these steps to get the backend running for local development.

### 1. Set Up Virtual Environment

Create and activate a virtual environment using `uv`:

```bash
# From the backend/ directory
uv venv
```

### 2. Install Dependencies

Install the required Python packages:

```bash
uv sync
```

To install the development dependencies for running tests, use:

```bash
uv sync --all-groups
```

### 3. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Next, **edit the `.env` file** to configure the application. At a minimum, you must provide the connection string for your external PostgreSQL database:

```env
DATABASE_URL="postgresql+asyncpg://user:password@host:port/dbname"
```

List-style settings like `CORS_ORIGINS` and `ALLOWED_HOSTS` can be a comma-separated string or a JSON array.

### 4. Database Migrations

With your database connection configured, apply the database migrations to set up the schema:

```bash
uv run alembic upgrade head
```

## Running the Server with a single command

To simplify the process of getting the backend running, you can use the `start_backend.sh` script. This script will:

1.  Create a virtual environment.
2.  Set up environment variables.
3.  Install dependencies.
4.  Run database migrations.
5.  Start the development server.

To run the script, first make it executable:

```bash
chmod +x start_backend.sh
```

Then, execute the script:

```bash
./start_backend.sh
```

## Running the Server

To start the development server, run:

```bash
# From the backend/ directory
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

### API Endpoints

-   **Health Check:** `http://localhost:8000/health`
-   **Swagger UI (API Docs):** `http://localhost:8000/docs`
-   **ReDoc:** `http://localhost:8000/redoc`

## Deploying to Google Cloud Run

This project is configured for a single Cloud Run service. The repo-root `Dockerfile` builds the exported Next.js frontend, copies it into `backend/static/`, installs the FastAPI backend, and runs:

```bash
uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
```

Cloud Run sets `PORT`; the image defaults to `8080` for local container runs.

### Runtime services

-   **Database:** CockroachDB. Provide either `DATABASE_URL` or the Postgres-compatible parts (`POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_SSL_MODE`).
-   **Cache:** Redis Cloud. Prefer `REDIS_URL` (for example `rediss://default:<password>@<host>:<port>/0` when TLS is required).
-   **Domain:** Use Cloud Run domain mapping for the custom domain, then set `HOST`, `CORS_ORIGINS`, and `ALLOWED_HOSTS` to that domain.

### GitHub Actions deployment

The workflow at `.github/workflows/deploy-cloud-run.yml` runs tests, verifies the container build, pushes the image to Artifact Registry, and deploys Cloud Run on `main` or manual dispatch.

Configure these GitHub repository variables:

```text
GCP_PROJECT_ID
GCP_REGION
GAR_REPOSITORY
CLOUD_RUN_SERVICE
GCP_WORKLOAD_IDENTITY_PROVIDER
GCP_SERVICE_ACCOUNT
HOST
CORS_ORIGINS
ALLOWED_HOSTS
NEXT_PUBLIC_GOOGLE_CLIENT_ID
GITHUB_CLIENT_ID
NOTION_CLIENT_ID
GOOGLE_CLIENT_ID
GOOGLE_OAUTH_SCOPES
OPENROUTER_BASE_URL
OPENROUTER_DEFAULT_MODEL
OPENROUTER_FALLBACK_MODELS
```

Configure these GitHub repository secrets as needed:

```text
DATABASE_URL
REDIS_URL
SECRET_KEY
GITHUB_CLIENT_SECRET
GITHUB_TOKEN
NOTION_CLIENT_SECRET
NOTION_TOKEN
GOOGLE_CLIENT_SECRET
GOOGLE_REFRESH_TOKEN
GOOGLE_CALENDAR_ACCESS_TOKEN
GMAIL_ACCESS_TOKEN
OPENROUTER_API_KEY
```

If you do not use `DATABASE_URL`, set the individual `POSTGRES_*` secrets instead.

### Manual deployment shape

The GitHub workflow automates this, but the equivalent flow is:

```bash
docker build -t REGION-docker.pkg.dev/PROJECT/REPOSITORY/SERVICE:latest .
docker push REGION-docker.pkg.dev/PROJECT/REPOSITORY/SERVICE:latest
gcloud run deploy SERVICE \
  --image REGION-docker.pkg.dev/PROJECT/REPOSITORY/SERVICE:latest \
  --region REGION \
  --allow-unauthenticated \
  --port 8080
```

Run Alembic migrations against CockroachDB from a controlled environment (for example a gated GitHub Actions job or local admin session), not automatically on every container start.

## Running Tests

To run the test suite, use `pytest`:

```bash
# Ensure dev dependencies are installed (uv sync --all-groups)
uv run pytest
```

Tests will use the configuration from your `.env` file. Integration tests that call external services (like GitHub or Notion) will be skipped unless you provide the necessary API keys in your `.env` file. To run only the live-marked tests, use: `uv run pytest -m live`.

## MCP Tool APIs

The MCP (Multi-tool Control Protocol) system allows the agent to interact with external tools and services.

-   `GET /api/v1/mcp/servers`: Lists registered integrations (e.g., GitHub, Notion) and their configuration status.
-   `GET /api/v1/mcp/tools`: Provides a catalog of available tools for each integration.
-   `POST /api/v1/mcp/invoke`: Executes a specific tool with the given arguments.

For detailed instructions on using these endpoints and configuring secrets for services like GitHub, Notion, and Google, refer to the sample payloads in `samples/mcp_invoke_payloads.json`.
