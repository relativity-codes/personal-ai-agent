import type { ActivityItem, DashboardStats, McpServer, RecentPlan } from "./types";

export const DEMO_STATS: DashboardStats = {
  total_requests: 45,
  total_plans: 12,
  connected_tools: 3,
  success_rate: 98,
};

export const DEMO_ACTIVITY: ActivityItem[] = [
  {
    id: "a1",
    action: "chat",
    intent_type: "agenda_preparation",
    success: true,
    created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    execution_time_ms: 2400,
  },
  {
    id: "a2",
    action: "chat",
    intent_type: "pr_management",
    success: true,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
    execution_time_ms: 3100,
  },
  {
    id: "a3",
    action: "chat",
    intent_type: "email_summary",
    success: false,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    execution_time_ms: 5200,
  },
  {
    id: "a4",
    action: "chat",
    intent_type: "calendar_check",
    success: true,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 26).toISOString(),
    execution_time_ms: 1800,
  },
];

export const DEMO_RECENT_PLANS: RecentPlan[] = [
  {
    id: "abc123",
    intent_type: "agenda_preparation",
    status: "completed",
    created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    completed_at: new Date(Date.now() - 1000 * 60 * 28).toISOString(),
  },
  {
    id: "def456",
    intent_type: "pr_management",
    status: "completed",
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
    completed_at: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString(),
  },
  {
    id: "ghi789",
    intent_type: "email_summary",
    status: "failed",
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    completed_at: null,
  },
];

export const DEMO_MCP_SERVERS: McpServer[] = [
  { name: "github", configured: true },
  { name: "notion", configured: true },
  { name: "calendar", configured: true },
  { name: "gmail", configured: false },
];
