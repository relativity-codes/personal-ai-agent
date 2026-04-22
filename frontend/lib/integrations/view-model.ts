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

export function getIntegrationStatusDetail(vm: IntegrationViewModel): string | undefined {
  if (!vm.connected) return undefined;
  if (vm.accountLabel) {
    if (vm.id === "github") return `Connected as ${vm.accountLabel}`;
    if (vm.id === "notion") return `Connected to "${vm.accountLabel}"`;
    return vm.accountLabel;
  }
  return vm.connectedExampleLabel;
}

export function mergeServersIntoDefinitions(servers: McpServerDTO[]): IntegrationViewModel[] {
  const byId = new Map<IntegrationId, McpServerDTO>();

  for (const server of servers) {
    const id = resolveIntegrationId(server.name);
    if (id) byId.set(id, server);
  }

  return INTEGRATION_DEFINITIONS.map((def) => {
    const match = byId.get(def.id);
    return {
      ...def,
      connected: match?.connected ?? false,
      lastSync: match?.last_sync,
      accountLabel: match?.account_label,
      permissionsLabel: match?.permissions ?? def.defaultPermissionsLabel,
    };
  });
}
