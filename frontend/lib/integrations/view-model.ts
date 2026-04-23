import { INTEGRATION_DEFINITIONS } from "./constants";
import { normalizeServerKey } from "./api";
import type { IntegrationId, IntegrationViewModel, McpServerDTO } from "./types";

const ID_ALIASES: Record<string, IntegrationId> = {
  github: "github",
  notion: "notion",
  calendar: "calendar",
  googlecalendar: "calendar",
  gmail: "gmail",
};

function resolveIntegrationId(raw: string): IntegrationId | undefined {
  const key = normalizeServerKey(raw);
  return ID_ALIASES[key];
}

function resolveServerToIntegrationId(server: McpServerDTO): IntegrationId | undefined {
  const fromApiId = server.id?.trim().toLowerCase();
  if (fromApiId === "github" || fromApiId === "notion" || fromApiId === "calendar" || fromApiId === "gmail") {
    return fromApiId;
  }
  return resolveIntegrationId(server.name);
}

export function getIntegrationStatusDetail(vm: IntegrationViewModel): string | undefined {
  if (!vm.configured) return undefined;
  if (vm.accountLabel) {
    if (vm.id === "github") return `Configured as ${vm.accountLabel}`;
    if (vm.id === "notion") return `Configured for "${vm.accountLabel}"`;
    return vm.accountLabel;
  }
  return vm.configuredStatusHint;
}

export function mergeServersIntoDefinitions(servers: McpServerDTO[]): IntegrationViewModel[] {
  const byId = new Map<IntegrationId, McpServerDTO>();

  for (const server of servers) {
    const id = resolveServerToIntegrationId(server);
    if (id) byId.set(id, server);
  }

  return INTEGRATION_DEFINITIONS.map((def) => {
    const match = byId.get(def.id);
    return {
      ...def,
      configured: match?.configured ?? false,
      lastSync: match?.last_sync,
      accountLabel: match?.account_label,
      permissionsLabel: match?.permissions ?? def.defaultPermissionsLabel,
    };
  });
}
