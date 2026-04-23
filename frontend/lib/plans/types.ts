export type PlanStatus = "pending" | "running" | "completed" | "failed";

export type PlanTask = {
  id: string;
  step: number;
  description: string;
  mcp_server: string;
  tool: string;
  parameters: Record<string, unknown>;
  depends_on: string[] | null;
  status: PlanStatus;
  result: unknown | null;
  error: string | null;
  created_at: string;
  updated_at: string | null;
};

export type Plan = {
  id: string;
  user_id: string;
  session_id: string;
  intent_type: string;
  status: PlanStatus;
  task_status: Record<string, string>;
  task_results: Record<string, unknown>;
  task_errors: Record<string, string>;
  execution_order: string[];
  created_at: string;
  updated_at: string | null;
  completed_at: string | null;
  tasks: PlanTask[];
};

export type PlanStatusResponse = {
  plan_id: string;
  status: PlanStatus;
  intent: string;
  tasks: PlanTask[];
  task_status: Record<string, string>;
  task_results: Record<string, unknown>;
  created_at: string;
  completed_at: string | null;
};
