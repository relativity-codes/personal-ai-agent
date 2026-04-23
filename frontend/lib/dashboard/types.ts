export type DashboardStats = {
  total_requests: number;
  total_plans: number;
  connected_tools: number;
  success_rate: number;
};

export type ActivityItem = {
  id: string;
  action: string;
  intent_type: string | null;
  success: boolean;
  created_at: string;
  execution_time_ms: number | null;
};

export type RecentPlan = {
  id: string;
  intent_type: string;
  status: string;
  created_at: string;
  completed_at: string | null;
};

export type McpServer = {
  name: string;
  configured: boolean;
  last_sync?: string;
};
