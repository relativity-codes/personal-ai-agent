# Personal AI Agent

Monorepo with a **FastAPI** backend (`backend/`) and a **Next.js** frontend (`frontend/`).

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python 3.11+)
- [Node.js](https://nodejs.org/) and [Yarn](https://yarnpkg.com/getting-started/install) (Classic or Berry)

## Environment

Copy the example env files once:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

Adjust `backend/.env` and `frontend/.env.local` as needed. The frontend uses `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`) to reach the API.

## Run both apps

Use **two terminals** from the repository root.

### 1. Backend (port 8000)

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health: [http://localhost:8000/health](http://localhost:8000/health)
- MCP: `GET /api/v1/mcp/servers`, `GET /api/v1/mcp/tools`, `POST /api/v1/mcp/invoke` (details in [backend/README.md](backend/README.md))

See [backend/README.md](backend/README.md) for tests, env vars, and Alembic.

### 2. Frontend (port 3000)

```bash
cd frontend
yarn install
yarn dev
```

Open [http://localhost:3000](http://localhost:3000).

More detail: [frontend/README.md](frontend/README.md).

## Production build (frontend)

```bash
cd frontend
yarn install
yarn build
yarn start
```
