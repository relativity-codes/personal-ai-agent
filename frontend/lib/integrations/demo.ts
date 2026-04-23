import type { McpServerDTO } from "./types";

/** Wireframe-like sample data when the API is unavailable (local dev / design review). */
export const DEMO_MCP_SERVERS: McpServerDTO[] = [
  {
    id: "github",
    name: "GitHub",
    configured: true,
    last_sync: new Date().toISOString(),
    account_label: "@username",
    permissions: "Read repos, read PRs, write issues",
  },
  {
    id: "notion",
    name: "Notion",
    configured: true,
    last_sync: new Date().toISOString(),
    account_label: "Personal Workspace",
  },
  { id: "calendar", name: "Google Calendar", configured: false },
  { id: "gmail", name: "Gmail", configured: false },
];
