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
