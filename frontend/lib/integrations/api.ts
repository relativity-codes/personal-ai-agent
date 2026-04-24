/* eslint-disable @typescript-eslint/no-explicit-any */
import { apiFetch } from "@/lib/api/client";
import type { IntegrationId, McpServersResponse, McpOauthStatus } from "./types";
import type { ApiResult } from "@/lib/api/types";

export async function fetchMcpServers(): Promise<McpServersResponse> {
  const result = await apiFetch<McpServersResponse>("/api/v1/mcp/servers");
  if (!result.success) {
    throw new Error(result.error);
  }
  return result.data;
}

export async function disconnectMcpServer(integrationId: IntegrationId): Promise<void> {
  const result = await apiFetch(`/api/v1/mcp/${integrationId}/disconnect`, {
    method: "POST",
  });
  if (!result.success) {
    throw new Error(result.error);
  }
}

export async function fetchMcpOauthStatus(): Promise<ApiResult<McpOauthStatus>> {
  return apiFetch<McpOauthStatus>("/api/v1/mcp/oauth/status");
}

export async function fetchAuthorizeUrl(provider: string, redirectUri: string): Promise<ApiResult<{ url: string }>> {
  const encodedUri = encodeURIComponent(redirectUri);
  return apiFetch<{ url: string }>(`/api/v1/mcp/oauth/${provider}/authorize-url?redirect_uri=${encodedUri}`);
}

export async function exchangeOAuthCode(provider: string, code: string, redirectUri: string): Promise<ApiResult<any>> {
  return apiFetch(`/api/v1/mcp/oauth/${provider}/token`, {
    method: "POST",
    body: JSON.stringify({ code, redirect_uri: redirectUri }),
  });
}

export function normalizeServerKey(name: string): string {
  return name.trim().toLowerCase().replace(/\s+/g, "");
}
