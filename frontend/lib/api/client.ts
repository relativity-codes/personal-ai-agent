import type { ApiResult } from "./types";

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
      } catch {
        // Fallback to generic status error
      }
      return { success: false, error: errorMessage };
    }

    const data = (await response.json()) as T;
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error instanceof Error ? error.message : String(error) };
  }
}
