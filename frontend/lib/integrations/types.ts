export type IntegrationId = "github" | "notion" | "calendar" | "gmail";

export type McpServerDTO = {
  name: string;
  connected: boolean;
  last_sync?: string;
  /** Optional account/workspace label when backend provides it */
  account_label?: string;
  /** Optional human-readable permissions summary */
  permissions?: string;
};

export type McpServersResponse = {
  servers: McpServerDTO[];
};

export type IntegrationDefinition = {
  id: IntegrationId;
  title: string;
  description: string;
  /** Shown when connected if API does not return account_label */
  connectedExampleLabel: string;
  /** Shown when connected if API does not return permissions */
  defaultPermissionsLabel?: string;
};

export type IntegrationViewModel = IntegrationDefinition & {
  connected: boolean;
  lastSync?: string;
  accountLabel?: string;
  permissionsLabel?: string;
};
