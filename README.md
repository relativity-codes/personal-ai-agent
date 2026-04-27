# Personal AI Agent

Monorepo with a **FastAPI** backend (`backend/`) and a **Next.js** frontend (`frontend/`).

## Getting Started

This guide will walk you through setting up the project for development. You can either follow the manual setup process or use the automated script.

### Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python 3.11+)
- [Node.js](https://nodejs.org/) and [Yarn](https://yarnpkg.com/getting-started/install) (Classic or Berry)
- [Docker](https://www.docker.com/get-started) (for running the database)

### Automated Setup

A bash script is provided to automate the setup process. The script will:

1.  Install backend and frontend dependencies.
2.  Set up the environment variables.
3.  Start the database using Docker Compose.
4.  Apply database migrations.
5.  Start the backend and frontend servers.

To run the script, execute the following command from the root of the project:

```bash
bash start_project.sh
```

### Manual Setup

If you prefer to set up the project manually, follow these steps:

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

The project uses a PostgreSQL database, which can be run with Docker Compose. From the project root, start the database:

```bash
docker-compose up -d
```

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

Use two separate terminals to run the backend and frontend servers.

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
```

## Production Endpoint

- App: https://personal-ai-agent-k5epd6zwva-uc.a.run.app
- Health check: https://personal-ai-agent-k5epd6zwva-uc.a.run.app/health
- API docs: https://personal-ai-agent-k5epd6zwva-uc.a.run.app/docs
