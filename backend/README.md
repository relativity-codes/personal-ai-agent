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

## Deploy with Zappa (AWS Lambda)

The backend can be deployed with [Zappa](https://github.com/zappa/Zappa) as an ASGI app on API Gateway and Lambda.

### Prerequisites

- AWS CLI configured (`aws configure`) with permissions to create Lambda, API Gateway, IAM roles, and S3 objects.
- An **S3 bucket** in the same account and region as the deployment, used only for Zappa to upload deployment packages. Replace `REPLACE_WITH_A_GLOBALLY_UNIQUE_S3_BUCKET_NAME` in `zappa_settings.json` with that bucket name (create it first if needed).

### Install Zappa

```bash
uv sync --group deploy
```

### Configure Lambda environment

Zappa does not read your local `.env`. Set production secrets and URLs in `zappa_settings.json` under `environment_variables`, or attach them later in the AWS Lambda console. At minimum you need the same variables as local development: PostgreSQL, Redis, auth keys, optional API keys, and:

- `ALLOWED_HOSTS` — include your API Gateway host (for example `*.execute-api.us-east-1.amazonaws.com` and any custom domain).
- `CORS_ORIGINS` — your deployed frontend origin(s).

Apply database schema with Alembic against your production database before sending traffic (for example run `uv run alembic upgrade head` from CI or your machine, pointed at production).

### Commands (from `backend/`)

```bash
# First deployment
uv run zappa deploy production

# Subsequent code updates
uv run zappa update production

# Logs
uv run zappa tail production
```

### Limitations

- Zappa’s ASGI bridge does **not** run FastAPI lifespan; this app uses idempotent startup middleware so database and Redis still initialize on Lambda.
- **WebSockets** (`/ws/...`) are not supported through Zappa’s default ASGI path; use a separate service (for example ECS) if you need chat WebSockets in production.
- Deployment package size and cold starts: this project has many dependencies; watch the Lambda deployment package size limit and consider `exclude` / slim packaging if needed.
- Packaging runs on your local machine and pulls manylinux wheels for Lambda’s Linux runtime; slow networks or timeouts can fail `zappa package` / `deploy`. Retry, or run deploy from a Linux CI host (or Zappa’s Docker-based workflow) if packaging is unreliable.

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
