#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Environment Setup ---
echo "Setting up environment variables..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
fi
if [ ! -f frontend/.env.local ]; then
    cp frontend/.env.example frontend/.env.local
fi
echo "IMPORTANT: Ensure your backend/.env file is configured to connect to your external database."
echo "Environment variables set up."

# --- Dependency Installation ---
echo "Installing backend dependencies..."
(cd backend && uv sync)
echo "Backend dependencies installed.

echo "Installing frontend dependencies..."
(cd frontend && yarn install)
echo "Frontend dependencies installed."

# --- Database Migrations ---
echo "Running database migrations..."
(cd backend && uv run alembic upgrade head)
echo "Database migrations applied."

# --- Start Servers ---
echo "Starting backend server..."
(cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000) &

echo "Starting frontend server..."
(cd frontend && yarn dev) &

wait
