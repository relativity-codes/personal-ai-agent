#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Setting up Backend Virtual Environment ---"
(cd backend && uv venv)
echo "Virtual environment ready."

echo "--- Installing Backend Dependencies ---"
(cd backend && uv sync)
echo "Backend dependencies installed."

echo "--- Setting up Environment Variables ---"
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "backend/.env created."
fi
echo "IMPORTANT: Ensure your backend/.env file is configured to connect to your external database."
echo "Environment variables checked."


echo "--- Running Database Migrations ---"
echo "Attempting to run migrations against the external database..."
(cd backend && uv run alembic upgrade head)
echo "Database migrations applied."

echo "--- Building Frontend ---"
(cd frontend && yarn install && yarn build)
echo "Frontend build complete."


echo "--- Copying Frontend to Backend Static Directory ---"
STATIC_DIR="backend/static"
rm -rf $STATIC_DIR
mkdir -p $STATIC_DIR
cp -r frontend/out/* $STATIC_DIR/
echo "Frontend files copied to $STATIC_DIR."

echo "--- Starting Single-App Server ---"
echo "The application will be available at http://localhost:8000"
(cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000)
