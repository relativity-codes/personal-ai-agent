import { getApiBaseUrl } from "@/lib/api/client";
import type { IntegrationId, McpServersResponse } from "./types";

function joinUrl(base: string, path: string): string {
  const b = base.replace(/\/$/, "");
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${b}${p}`;
}

export function getMcpAuthUrl(integrationId: IntegrationId): string {
  return joinUrl(getApiBaseUrl(), `/api/v1/mcp/${integrationId}/auth`);
}

export function getMcpDisconnectUrl(integrationId: IntegrationId): string {
  return joinUrl(getApiBaseUrl(), `/api/v1/mcp/${integrationId}/disconnect`);
}

export function getMcpServersUrl(): string {
  return joinUrl(getApiBaseUrl(), "/api/v1/mcp/servers");
}

export function normalizeServerKey(name: string): string {
  return name.trim().toLowerCase().replace(/\s+/g, "");
}

export async function fetchMcpServers(): Promise<McpServersResponse> {
  const res = await fetch(getMcpServersUrl(), {
    method: "GET",
    headers: { Accept: "application/json" },
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(`Failed to load integrations (${res.status})`);
  }

  return (await res.json()) as McpServersResponse;
}

export async function disconnectMcpServer(integrationId: IntegrationId): Promise<void> {
  const res = await fetch(getMcpDisconnectUrl(integrationId), {
    method: "POST",
    headers: { Accept: "application/json" },
  });

  if (!res.ok) {
    throw new Error(`Failed to disconnect (${res.status})`);
  }
}
