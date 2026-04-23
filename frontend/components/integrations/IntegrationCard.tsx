"use client";

import { useMemo, useState } from "react";
import type { IntegrationViewModel } from "@/lib/integrations/types";
import { disconnectMcpServer } from "@/lib/integrations/api";
import { getIntegrationStatusDetail } from "@/lib/integrations/view-model";
import { ConnectionStatusBadge } from "./ConnectionStatusBadge";
import { ConfigureButton } from "./ConfigureButton";
import { DisconnectButton } from "./DisconnectButton";
import { IntegrationLogo } from "./IntegrationLogo";
import { OAuthButton } from "./OAuthButton";

type Props = {
  model: IntegrationViewModel;
  onConfigure: (model: IntegrationViewModel) => void;
  onRefresh: () => Promise<void>;
};

export function IntegrationCard({ model, onConfigure, onRefresh }: Props) {
  const [busy, setBusy] = useState<"disconnect" | null>(null);
  const [banner, setBanner] = useState<string | null>(null);

  const statusDetail = useMemo(() => getIntegrationStatusDetail(model), [model]);

  async function handleDisconnect() {
    const ok = window.confirm(`Disconnect ${model.title}? This may remove access for automations that rely on it.`);
    if (!ok) return;

    setBusy("disconnect");
    setBanner(null);
    try {
      await disconnectMcpServer(model.id);
      await onRefresh();
    } catch (e) {
      const message = e instanceof Error ? e.message : "Could not disconnect. Please try again.";
      setBanner(message);
    } finally {
      setBusy(null);
    }
  }

  return (
    <section
      className="rounded-2xl border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-950"
      aria-label={`${model.title} integration`}
    >
      <div className="p-5 sm:p-7">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex min-w-0 gap-4">
            <IntegrationLogo id={model.id} />
            <div className="min-w-0">
              <h2 className="text-base font-semibold tracking-tight text-zinc-900 dark:text-zinc-50 sm:text-lg">
                {model.title}
              </h2>
              <p className="mt-2 max-w-prose text-sm leading-relaxed text-zinc-600 dark:text-zinc-300">
                {model.description}
              </p>
            </div>
          </div>
        </div>

        <div className="mt-6 space-y-3 rounded-xl bg-zinc-50 p-4 dark:bg-zinc-900/40 sm:p-5">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div className="text-sm text-zinc-700 dark:text-zinc-200">
              <div className="flex flex-wrap items-center gap-x-3 gap-y-2">
                <span className="font-medium text-zinc-900 dark:text-zinc-50">Status</span>
                <ConnectionStatusBadge connected={model.connected} />
              </div>
              {model.connected && statusDetail ? (
                <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-300">{statusDetail}</p>
              ) : null}
            </div>
          </div>

          {model.connected && model.permissionsLabel ? (
            <p className="text-sm leading-relaxed text-zinc-600 dark:text-zinc-300">
              <span className="font-medium text-zinc-800 dark:text-zinc-100">Permissions: </span>
              {model.permissionsLabel}
            </p>
          ) : null}

          {model.lastSync ? (
            <p className="text-xs text-zinc-500 dark:text-zinc-400">
              Last sync:{" "}
              <time dateTime={model.lastSync}>
                {new Intl.DateTimeFormat("en-US", { dateStyle: "medium", timeStyle: "short" }).format(
                  new Date(model.lastSync),
                )}
              </time>
            </p>
          ) : null}
        </div>

        {banner ? (
          <div
            className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-900 dark:border-red-900/60 dark:bg-red-950/40 dark:text-red-100"
            role="alert"
          >
            {banner}
          </div>
        ) : null}

        <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
          {model.connected ? (
            <>
              <ConfigureButton onClick={() => onConfigure(model)} disabled={busy !== null} />
              <DisconnectButton onClick={() => void handleDisconnect()} busy={busy === "disconnect"} />
            </>
          ) : (
            <OAuthButton integrationId={model.id} busy={false} disabled={busy !== null} />
          )}
        </div>
      </div>
    </section>
  );
}
