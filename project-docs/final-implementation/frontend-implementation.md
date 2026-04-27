# Frontend Implementation

## Summary

The frontend is a Next.js 14 App Router application in [`../../frontend`](../../frontend). It is configured as a static export and is served by the FastAPI backend in production.

## Frontend Folder Structure

```text
frontend/
├── app/
│   ├── (auth)/                    # Sign-in pages
│   └── (app)/                     # Main product routes
├── components/
│   ├── auth/                      # SignIn and auth UI
│   └── shared/                    # Shared navigation/layout
├── lib/
│   ├── api/
│   │   └── client.ts              # apiFetch and API base logic
│   ├── chat/
│   │   └── websocket.ts           # WS transport wrapper
│   ├── hooks/
│   │   ├── useChat.ts             # Chat state/orchestration
│   │   └── useAuth.ts             # User bootstrap hook
│   └── store/
│       └── userStore.ts           # Zustand persisted user state
└── next.config.mjs                # Static export configuration
```

## Route Structure

The application uses the App Router with static pages.

Primary routes:

- `/`: landing page.
- `/sign-in`: Google sign-in page.
- `/dashboard`: main authenticated dashboard.
- `/chat`: chat interface for agent interaction.
- `/integrations`: integration status and connection UI.
- `/integrations/callback`: OAuth callback handling page.
- `/plans`: execution plan list.
- `/plans/detail`: plan detail page.
- `/activity`: activity/audit view.
- `/help`: help page.
- `/settings/profile`, `/settings/preferences`, `/settings/tokens`: settings views.

Because the project is statically exported, route protection is primarily enforced by the backend API rather than by server-side Next.js middleware.

## Static Export

[`../../frontend/next.config.mjs`](../../frontend/next.config.mjs) sets:

- `output: "export"`
- `trailingSlash: true`
- `images.unoptimized: true`

The production Docker build runs the frontend build and copies `frontend/out` into the backend image as `/app/static`. FastAPI then serves the static app from its catch-all route.

## API Client

The API helper in [`../../frontend/lib/api/client.ts`](../../frontend/lib/api/client.ts) centralizes REST calls.

Important behavior:

- `NEXT_PUBLIC_API_URL` controls the API base URL.
- An empty `NEXT_PUBLIC_API_URL` makes API calls relative to the same origin, which is the intended Cloud Run deployment mode.
- Responses are wrapped in an `ApiResult<T>` shape with `success`, `data`, and `error`.
- Error responses trigger Sonner toast messages.

Reviewer caveat: the current helper places `"credentials": "include"` inside `headers`; browser `fetch` expects `credentials: "include"` on the options object. In the single-origin Cloud Run deployment, cookies are naturally sent for same-origin requests, but this should be corrected if cross-origin deployments are used.

## Authentication UX

The sign-in flow is implemented in [`../../frontend/components/auth/SignIn.tsx`](../../frontend/components/auth/SignIn.tsx).

Flow:

1. `GoogleOAuthProvider` renders the Google login button.
2. The browser receives a Google credential.
3. The frontend posts `{ id_token }` to `/api/v1/auth/google`.
4. The backend verifies the token and sets the `access_token` httpOnly cookie.
5. The frontend routes the user to `/dashboard`.

The Google client ID is provided at build time through `NEXT_PUBLIC_GOOGLE_CLIENT_ID`.

## User State

User state is held in a Zustand store with persistence. `useAuth` calls `/api/v1/users/me` through `apiFetch` and stores the result.

Reviewer caveat: `useAuth` currently treats the value returned by `apiFetch` like a raw user object even though `apiFetch` returns an `ApiResult<T>` wrapper. This is an implementation detail worth fixing before relying on the hook as the only route guard.

## Chat UX

Chat uses two paths:

- REST fallback: `POST /api/v1/chat/`
- WebSocket: `/ws/chat`

[`../../frontend/lib/chat/websocket.ts`](../../frontend/lib/chat/websocket.ts) builds the WebSocket URL from `NEXT_PUBLIC_API_URL`, falling back to `window.location.origin` for same-origin deployment. It switches `http` to `ws` and connects to `/ws/chat`.

[`../../frontend/lib/hooks/useChat.ts`](../../frontend/lib/hooks/useChat.ts) owns message state, WebSocket lifecycle, session creation handling, streamed graph steps, and REST fallback behavior.

## Integration UX

The integrations page talks to `/api/v1/mcp` endpoints to show available tool servers and connection state. OAuth callbacks are handled through the `/integrations/callback` page and backend MCP OAuth routes.

## Reviewer Notes

- The frontend is intentionally compatible with single-service deployment: static files and API share one origin.
- There is no Next.js server runtime in production; only the exported static files are served.
- Backend auth remains the source of truth for protected data.
- Cross-origin deployment would require extra care around cookie credentials, CORS, and `NEXT_PUBLIC_API_URL`.

