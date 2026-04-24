/* eslint-disable @typescript-eslint/no-explicit-any */
import { apiFetch } from "@/lib/api/client";
import type { ApiResult } from "@/lib/api/types";

export type AuditLog = {
  id: string;
  user_id: string;
  action: string;
  resource: string;
  resource_id?: string;
  details: Record<string, any>;
  success: boolean;
  error?: string;
  created_at: string;
};

export async function fetchAuditLogs(skip = 0, limit = 100): Promise<ApiResult<AuditLog[]>> {
  return apiFetch<AuditLog[]>(`/api/v1/audit-logs/?skip=${skip}&limit=${limit}`);
}

export async function fetchAuditLogById(logId: string): Promise<ApiResult<AuditLog>> {
  return apiFetch<AuditLog>(`/api/v1/audit-logs/${logId}`);
}
