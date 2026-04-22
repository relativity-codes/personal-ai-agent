import type { IntegrationDefinition } from "./types";

export const INTEGRATION_DEFINITIONS: readonly IntegrationDefinition[] = [
  {
    id: "github",
    title: "GitHub",
    description: "Connect to GitHub for PR management, commit summaries, and issue creation.",
    connectedExampleLabel: "Connected as @username",
    defaultPermissionsLabel: "Read repos, read PRs, write issues",
  },
  {
    id: "notion",
    title: "Notion",
    description: "Connect to Notion for page creation, database queries, and agenda extraction.",
    connectedExampleLabel: 'Connected to "Personal Workspace"',
  },
  {
    id: "calendar",
    title: "Google Calendar",
    description: "Connect to Google Calendar for event fetching, scheduling, and availability.",
    connectedExampleLabel: "Connected to Google Calendar",
  },
  {
    id: "gmail",
    title: "Gmail",
    description: "Connect to Gmail for email summarization, thread analysis, and action extraction.",
    connectedExampleLabel: "Connected to Gmail",
  },
] as const;
