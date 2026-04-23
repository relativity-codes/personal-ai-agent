# Frontend

This directory contains the Next.js web application that provides the user interface for the Personal AI Agent.

## Prerequisites

- Node.js 18+
- [Yarn](https://yarnpkg.com/getting-started/install)

## Getting Started

Follow these steps to get the frontend running for local development.

### 1. Install Dependencies

From the `frontend/` directory, install the required packages using Yarn:

```bash
yarn install
```

### 2. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env.local
```

Next, **edit the `.env.local` file** to point to your running backend API. By default, it expects the backend to be at `http://localhost:8000`.

```env
# URL of the backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

If your backend is running on a different address or port, make sure to update this value.

## Running the Development Server

To start the Next.js development server, run:

```bash
yarn dev
```

The application will be available at [http://localhost:3000](http://localhost:3000). The page will automatically reload if you make any edits.

## Building for Production

To create a production-ready build of the application for static export, run:

```bash
yarn build
```

This will generate a static site in the `out` directory. This is the directory used by the `build_and_serve.sh` script to serve the frontend from the backend.

## Linting

To check the code for style and potential errors, run the linter:

```bash
yarn lint
```
