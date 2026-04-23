import { getApiBaseUrl } from "@/lib/api/client";
import type { ApiResult } from "@/lib/api/types";
import {
  DEMO_ACTIVITY,
  DEMO_MCP_SERVERS,
  DEMO_RECENT_PLANS,
  DEMO_STATS,
} from "./demo";
import type { ActivityItem, DashboardStats, McpServer, RecentPlan } from "./types";

async function apiFetch<T>(path: string): Promise<ApiResult<T>> {
  try {
    const res = await fetch(`${getApiBaseUrl()}${path}`, { cache: "no-store" });
    if (!res.ok) return { success: false, error: `HTTP ${res.status}` };
    const data = (await res.json()) as T;
    return { success: true, data };
  } catch (e) {
    return { success: false, error: String(e) };
  }
}

export async function fetchDashboardStats(): Promise<DashboardStats> {
  const [plansResult, activityResult] = await Promise.all([
    apiFetch<unknown[]>("/api/v1/plans/?skip=0&limit=100"),
    apiFetch<unknown[]>("/api/v1/audit-logs/?skip=0&limit=100"),
  ]);

  if (!plansResult.success || !activityResult.success) return DEMO_STATS;

  const plans = plansResult.data as Array<{ status: string }>;
  const logs = activityResult.data as Array<{ success: boolean }>;
  const successCount = logs.filter((l) => l.success).length;

  return {
    total_requests: logs.length,
    total_plans: plans.length,
    connected_tools: DEMO_STATS.connected_tools,
    success_rate: logs.length > 0 ? Math.round((successCount / logs.length) * 100) : 100,
  };
}

export async function fetchRecentActivity(limit = 5): Promise<ActivityItem[]> {
  const result = await apiFetch<ActivityItem[]>(
    `/api/v1/audit-logs/?skip=0&limit=${limit}`
  );
  return result.success ? result.data : DEMO_ACTIVITY.slice(0, limit);
}

export async function fetchRecentPlans(limit = 5): Promise<RecentPlan[]> {
  const result = await apiFetch<RecentPlan[]>(
    `/api/v1/plans/?skip=0&limit=${limit}`
  );
  return result.success ? result.data : DEMO_RECENT_PLANS.slice(0, limit);
}

export async function fetchMcpServers(): Promise<McpServer[]> {
  const result = await apiFetch<{ servers?: McpServer[] } | McpServer[]>(
    "/api/v1/mcp/servers"
  );
  if (!result.success) return DEMO_MCP_SERVERS;
  const raw = result.data;
  if (Array.isArray(raw)) return raw;
  if (raw && typeof raw === "object" && "servers" in raw && Array.isArray(raw.servers))
    return raw.servers;
  return DEMO_MCP_SERVERS;
}
