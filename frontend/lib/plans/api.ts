/* eslint-disable @typescript-eslint/no-explicit-any */
import { apiFetch } from "@/lib/api/client";
import type { ApiResult } from "@/lib/api/types";
import type { Plan, PlanStatusResponse } from "./types";

export async function fetchPlans(skip = 0, limit = 20): Promise<ApiResult<Plan[]>> {
  return apiFetch<Plan[]>(`/api/v1/plans/?skip=${skip}&limit=${limit}`);
}

export async function fetchPlanById(planId: string): Promise<ApiResult<Plan>> {
  return apiFetch<Plan>(`/api/v1/plans/${planId}`);
}

export async function fetchPlanStatus(planId: string): Promise<ApiResult<PlanStatusResponse>> {
  return apiFetch<PlanStatusResponse>(`/api/v1/agents/${planId}/status`);
}

export async function deletePlan(planId: string): Promise<ApiResult<boolean>> {
  return apiFetch<boolean>(`/api/v1/plans/${planId}`, {
    method: "DELETE",
  });
}

export async function updateTaskStatus(taskId: string, status: string): Promise<ApiResult<any>> {
  return apiFetch(`/api/v1/tasks/${taskId}`, {
    method: "PUT",
    body: JSON.stringify({ status }),
  });
}
