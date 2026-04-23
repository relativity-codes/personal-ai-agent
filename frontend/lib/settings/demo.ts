export type DemoProfile = {
  name: string;
  email: string;
  userId: string;
  memberSinceIso: string;
};

export const DEMO_PROFILE: DemoProfile = {
  name: "John Doe",
  email: "john@example.com",
  userId: "user_abc123",
  memberSinceIso: "2026-01-15T12:00:00.000Z",
};

export const WORKDAY_KEYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"] as const;

export const WORKDAY_LABELS: Record<(typeof WORKDAY_KEYS)[number], string> = {
  mon: "Mon",
  tue: "Tue",
  wed: "Wed",
  thu: "Thu",
  fri: "Fri",
  sat: "Sat",
  sun: "Sun",
};

export type DemoPreferences = {
  defaultGithubRepo: string;
  defaultNotionDb: string;
  timezone: string;
  workingStart: string;
  workingEnd: string;
  workingDays: Record<(typeof WORKDAY_KEYS)[number], boolean>;
  emailWeeklySummaries: boolean;
  notifyLongTasks: boolean;
  dailyDigest: boolean;
  defaultModel: string;
  responseStyle: "concise" | "detailed" | "auto";
  streaming: boolean;
  saveHistory: boolean;
};

export const DEMO_PREFERENCES: DemoPreferences = {
  defaultGithubRepo: "personal-ai-agent/backend",
  defaultNotionDb: "Daily Standups Database",
  timezone: "America/Los_Angeles",
  workingStart: "09:00",
  workingEnd: "17:00",
  workingDays: { mon: true, tue: true, wed: true, thu: true, fri: true, sat: false, sun: false },
  emailWeeklySummaries: true,
  notifyLongTasks: true,
  dailyDigest: false,
  defaultModel: "claude-3-5-sonnet",
  responseStyle: "auto",
  streaming: true,
  saveHistory: false,
};

export type DemoApiToken = {
  id: string;
  name: string;
  createdIso: string;
  lastUsedIso: string | null;
};

export const DEMO_API_TOKENS: DemoApiToken[] = [
  { id: "1", name: "CLI Token", createdIso: "2026-04-01T10:00:00.000Z", lastUsedIso: "2026-04-20T15:22:00.000Z" },
  { id: "2", name: "GitHub Action", createdIso: "2026-04-10T09:30:00.000Z", lastUsedIso: "2026-04-21T08:01:00.000Z" },
  { id: "3", name: "VSCode Extension", createdIso: "2026-04-15T18:45:00.000Z", lastUsedIso: null },
];

export const DEMO_TOKEN_USAGE = {
  requestsThisMonth: 45,
  requestsThisWeek: 12,
  successRatePct: 98,
} as const;
