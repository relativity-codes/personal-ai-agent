import type { IntegrationDefinition } from "./types";

export const INTEGRATION_DEFINITIONS: readonly IntegrationDefinition[] = [
  {
    id: "github",
    title: "GitHub",
    description: "Connect to GitHub for PR management, commit summaries, and issue creation.",
    configuredStatusHint: "Configured as @username",
    defaultPermissionsLabel: "Read repos, read PRs, write issues",
  },
  {
    id: "notion",
    title: "Notion",
    description: "Connect to Notion for page creation, database queries, and agenda extraction.",
    configuredStatusHint: 'Configured for workspace "Personal Workspace"',
  },
  {
    id: "calendar",
    title: "Google Calendar",
    description: "Connect to Google Calendar for event fetching, scheduling, and availability.",
    configuredStatusHint: "Google Calendar is configured",
  },
  {
    id: "gmail",
    title: "Gmail",
    description: "Connect to Gmail for email summarization, thread analysis, and action extraction.",
    configuredStatusHint: "Gmail is configured",
  },
] as const;
