#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Setup Virtual Environment ---
echo "Setting up virtual environment..."
uv venv
echo "Virtual environment set up."

# --- Environment Setup ---
echo "Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
fi
echo "IMPORTANT: Ensure your .env file is configured to connect to your external database."
echo "Environment variables set up."

# --- Dependency Installation ---
echo "Installing backend dependencies..."
uv sync
echo "Backend dependencies installed."

# --- Database Migrations ---
echo "Running database migrations..."
uv run alembic upgrade head
echo "Database migrations applied."

# --- Start Servers ---
echo "Starting backend server..."
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &

wait
