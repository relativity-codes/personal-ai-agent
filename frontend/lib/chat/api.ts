/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable @typescript-eslint/no-explicit-any */
import { apiFetch } from "@/lib/api/client";
import type { ApiResult } from "@/lib/api/types";
import type { ChatSession, ChatMessage } from "./types";

export async function fetchSessions(skip = 0, limit = 100): Promise<ApiResult<any[]>> {
  // Since we don't have a direct "get all my sessions" without user_id in the URL yet,
  // we might need to handle this. But backend has /user/{user_id}.
  // For now, let's assume we can fetch by a generic list if implemented or use a placeholder.
  return apiFetch<any[]>(`/api/v1/sessions/?skip=${skip}&limit=${limit}`);
}

export async function fetchSessionHistory(sessionId: string): Promise<ApiResult<any[]>> {
  return apiFetch<any[]>(`/api/v1/chat-history/session/${sessionId}`);
}

export async function fetchAllChatHistory(skip = 0, limit = 100): Promise<ApiResult<any[]>> {
  return apiFetch<any[]>(`/api/v1/chat-history/?skip=${skip}&limit=${limit}`);
}

export async function deleteSession(sessionId: string): Promise<ApiResult<boolean>> {
  return apiFetch<boolean>(`/api/v1/sessions/${sessionId}`, {
    method: "DELETE",
  });
}
