import { getApiBaseUrl } from "@/lib/api/client";
import type { ApiResult } from "@/lib/api/types";
import type { Plan, PlanStatusResponse } from "./types";

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

export async function fetchPlans(skip = 0, limit = 20): Promise<ApiResult<Plan[]>> {
  return apiFetch<Plan[]>(`/api/v1/plans/?skip=${skip}&limit=${limit}`);
}

export async function fetchPlanStatus(planId: string): Promise<ApiResult<PlanStatusResponse>> {
  return apiFetch<PlanStatusResponse>(`/api/v1/agents/${planId}/status`);
}
