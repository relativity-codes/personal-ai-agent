export type IntegrationId = "github" | "notion" | "calendar" | "gmail";

export type McpServerDTO = {
  /** Stable server id from the API (e.g. `github`). Prefer this for matching. */
  id?: string;
  name: string;
  configured: boolean;
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
  /** Shown when configured if API does not return account_label */
  configuredStatusHint: string;
  /** Shown when configured if API does not return permissions */
  defaultPermissionsLabel?: string;
};

export type IntegrationViewModel = IntegrationDefinition & {
  configured: boolean;
  lastSync?: string;
  accountLabel?: string;
  permissionsLabel?: string;
};

export type McpOauthStatus = {
  google: {
    oauth_client_configured: boolean;
    authorize_url_path: string;
    token_exchange_path: string;
  };
  github: {
    oauth_client_configured: boolean;
    authorize_url_path: string;
    token_exchange_path: string;
  };
  notion: {
    oauth_client_configured: boolean;
    authorize_url_path: string;
    token_exchange_path: string;
  };
};
