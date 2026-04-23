"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { fetchMcpServers } from "@/lib/integrations/api";
import { DEMO_MCP_SERVERS } from "@/lib/integrations/demo";
import { mergeServersIntoDefinitions } from "@/lib/integrations/view-model";
import type { IntegrationViewModel } from "@/lib/integrations/types";
import { PlanCardSkeleton } from "@/components/shared/loading/PlanCardSkeleton";
import { ConfigureModal } from "./ConfigureModal";
import { IntegrationCard } from "./IntegrationCard";
import { IntegrationsIntro } from "./IntegrationsIntro";

export function IntegrationsView() {
  const [models, setModels] = useState<IntegrationViewModel[]>(() => mergeServersIntoDefinitions(DEMO_MCP_SERVERS));
  const [loading, setLoading] = useState(true);
  const [usingDemoData, setUsingDemoData] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [configureTarget, setConfigureTarget] = useState<IntegrationViewModel | null>(null);

  const reload = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const res = await fetchMcpServers();
      setModels(mergeServersIntoDefinitions(res.servers));
      setUsingDemoData(false);
    } catch (e) {
      const message = e instanceof Error ? e.message : "Could not load integrations.";
      setLoadError(message);
      setModels(mergeServersIntoDefinitions(DEMO_MCP_SERVERS));
      setUsingDemoData(true);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void reload();
  }, [reload]);

  const configureOpen = useMemo(() => configureTarget !== null, [configureTarget]);

  return (
    <>
      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-10 lg:px-8">
        <IntegrationsIntro />

        {loadError && usingDemoData ? (
          <div
            className="mt-6 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950 dark:border-amber-900/50 dark:bg-amber-950/30 dark:text-amber-100"
            role="status"
          >
            <p className="font-medium">API unavailable — showing sample data</p>
            <p className="mt-1 text-sm opacity-90">{loadError}</p>
            <div className="mt-3">
              <button
                type="button"
                className="inline-flex min-h-[40px] items-center justify-center rounded-lg bg-amber-900 px-3 py-2 text-sm font-semibold text-white transition hover:bg-amber-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-700 disabled:opacity-60 dark:bg-amber-300 dark:text-amber-950 dark:hover:bg-amber-200 dark:focus-visible:outline-amber-200"
                onClick={() => void reload()}
                disabled={loading}
              >
                Retry
              </button>
            </div>
          </div>
        ) : null}

        {!usingDemoData && loading ? (
          <div className="mt-8 space-y-4" aria-busy="true" aria-live="polite">
            <p className="sr-only">Loading integrations</p>
            {Array.from({ length: 4 }).map((_, idx) => (
              <PlanCardSkeleton key={idx} className="h-[190px]" />
            ))}
          </div>
        ) : (
          <div className="mt-8 grid gap-5 lg:gap-6">
            {models.map((m) => (
              <IntegrationCard
                key={m.id}
                model={m}
                onConfigure={setConfigureTarget}
                onRefresh={reload}
              />
            ))}
          </div>
        )}
      </main>

      <ConfigureModal integration={configureTarget} open={configureOpen} onClose={() => setConfigureTarget(null)} />
    </>
  );
}
