/* eslint-disable @typescript-eslint/no-explicit-any */
import type { ApiResult } from "./types";
import { toast } from "sonner";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

export function getApiBaseUrl(): string {
  return API_BASE_URL;
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<ApiResult<T>> {
  const url = path.startsWith("http") ? path : `${API_BASE_URL}${path}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage = `Error ${response.status}`;
      try {
        const errorJson = JSON.parse(errorText);
        errorMessage = errorJson.detail || errorJson.message || errorMessage;
        
        // Handle specific case where detail is an object (like my recent backend fix)
        if (typeof errorMessage === "object" && errorMessage !== null) {
          errorMessage = (errorMessage as any).message || JSON.stringify(errorMessage);
        }
      } catch {
        // Fallback to generic status error
      }

      if (response.status === 401) {
        toast.error("Session expired. Please log in again.", { id: "auth-error" });
      } else {
        toast.error(errorMessage);
      }

      return { success: false, error: errorMessage };
    }

    const data = (await response.json()) as T;
    return { success: true, data };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    toast.error(errorMessage);
    return { success: false, error: errorMessage };
  }
}
