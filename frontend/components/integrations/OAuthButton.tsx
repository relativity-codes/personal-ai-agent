"use client";

import type { IntegrationId } from "@/lib/integrations/types";
import { getMcpAuthUrl } from "@/lib/integrations/api";

type Props = {
  integrationId: IntegrationId;
  disabled?: boolean;
  busy?: boolean;
};

export function OAuthButton({ integrationId, disabled, busy }: Props) {
  return (
    <button
      type="button"
      className="inline-flex w-full min-h-[44px] min-w-0 items-center justify-center gap-2 rounded-lg bg-zinc-900 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-zinc-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-900 disabled:cursor-not-allowed disabled:opacity-60 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200 dark:focus-visible:outline-zinc-200 sm:w-auto sm:min-w-[140px]"
      disabled={disabled || busy}
      aria-busy={busy || undefined}
      onClick={() => {
        window.location.assign(getMcpAuthUrl(integrationId));
      }}
    >
      {busy ? (
        <>
          <Spinner />
          Connecting
        </>
      ) : (
        <>
          Connect
          <span aria-hidden>→</span>
        </>
      )}
    </button>
  );
}

function Spinner() {
  return (
    <span
      className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white dark:border-zinc-900/30 dark:border-t-zinc-900"
      aria-hidden
    />
  );
}
