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

## Tests

```bash
cd backend
uv sync --all-groups
uv run pytest
```

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
