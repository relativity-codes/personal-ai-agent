# Personal AI Agent

Monorepo with a **FastAPI** backend (`backend/`) and a **Next.js** frontend (`frontend/`).

## Getting Started

This guide will walk you through setup and local run options. The recommended path is the root script `build_and_serve.sh`. The manual process below is mainly for developers who want fine-grained control.

### Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python 3.11+)
- [Node.js](https://nodejs.org/) and [Yarn](https://yarnpkg.com/getting-started/install) (Classic or Berry)
- PostgreSQL database access (local install or managed provider)

### Recommended: Single-Script Setup

Use `build_and_serve.sh` from the project root. It will:

1.  Create backend virtual environment (if missing).
2.  Install backend dependencies.
3.  Ensure `backend/.env` exists.
4.  Run Alembic migrations.
5.  Build frontend static assets.
6.  Copy frontend build output into `backend/static/`.
7.  Start a single FastAPI server that serves both API and frontend on port `8000`.

To run the script, execute the following command from the root of the project:

```bash
bash build_and_serve.sh
```

### Developer Workflow (Manual Setup)

If you are developing features/debugging and want full control over each step, use this manual workflow:

#### 1. Environment Setup

Copy the example environment files:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

Adjust the variables in `backend/.env` and `frontend/.env.local` as needed. The frontend uses `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`) to connect to the backend API.

#### 2. Dependency Installation

**Backend:**

```bash
cd backend
uv sync
```

**Frontend:**

```bash
cd frontend
yarn install
```

#### 3. Database Setup

The project uses PostgreSQL. You can choose whichever setup fits your environment:

- Local PostgreSQL installation
- Managed PostgreSQL-compatible provider (for example CockroachDB)

Then set the database values in `backend/.env` (`DATABASE_URL` or `POSTGRES_*` fields) to match your chosen setup.

#### 4. Database Migrations

With the database running, apply the migrations to create the necessary tables:

```bash
alembic upgrade head
```

If the `alembic` command is not found, you can run it from the backend's virtual environment:

```bash
uv run alembic upgrade head
```

#### 5. Running the Application

Use separate terminals to run backend and frontend in dev mode.

**Backend (port 8000):**

```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health check: [http://localhost:8000/health](http://localhost:8000/health)

**Frontend (port 3000):**

```bash
cd frontend
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Production Build (Frontend)

To create a production build of the frontend:

```bash
cd frontend
yarn install
yarn build
yarn start
<<<<<<< HEAD
```

## Production Endpoint

- App: https://personal-ai-agent-k5epd6zwva-uc.a.run.app
- Health check: https://personal-ai-agent-k5epd6zwva-uc.a.run.app/health
- API docs: https://personal-ai-agent-k5epd6zwva-uc.a.run.app/docs
=======
```
>>>>>>> main
