import type { McpServerDTO } from "./types";

/** Wireframe-like sample data when the API is unavailable (local dev / design review). */
export const DEMO_MCP_SERVERS: McpServerDTO[] = [
  {
    name: "github",
    connected: true,
    last_sync: new Date().toISOString(),
    account_label: "@username",
    permissions: "Read repos, read PRs, write issues",
  },
  {
    name: "notion",
    connected: true,
    last_sync: new Date().toISOString(),
    account_label: "Personal Workspace",
  },
  { name: "calendar", connected: false },
  { name: "gmail", connected: false },
];
