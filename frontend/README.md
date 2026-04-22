# Frontend

Next.js app (App Router). Package management uses **Yarn**.

## Prerequisites

- Node.js 18+
- [Yarn](https://yarnpkg.com/getting-started/install)

## Setup

From the `frontend` directory:

```bash
cp .env.example .env.local
yarn install
```

Set `NEXT_PUBLIC_API_URL` in `.env.local` if the API is not at `http://localhost:8000`.

## Run the dev server

```bash
yarn dev
```

Open [http://localhost:3000](http://localhost:3000).

## Build and production server

```bash
yarn build
yarn start
```

## Lint

```bash
yarn lint
```

## Monorepo

To run the API and this app together, see the [root README](../README.md).
