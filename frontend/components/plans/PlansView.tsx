"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { PlanCardSkeleton } from "@/components/shared/loading/PlanCardSkeleton";
import { StatsCardSkeleton } from "@/components/shared/loading/StatsCardSkeleton";
import { fetchPlans } from "@/lib/plans/api";
import type { Plan } from "@/lib/plans/types";
import { FilterBar } from "./FilterBar";
import { PlanCard } from "./PlanCard";

const PAGE_SIZE = 20;

function StatsCards({ plans }: { plans: Plan[] }) {
  const total = plans.length;
  const thisWeek = plans.filter((p) => {
    const d = new Date(p.created_at);
    const now = new Date();
    return now.getTime() - d.getTime() < 7 * 24 * 60 * 60 * 1000;
  }).length;
  const failed = plans.filter((p) => p.status === "failed").length;
  const completed = plans.filter((p) => p.status === "completed").length;
  const successRate = total > 0 ? Math.round((completed / total) * 100) : 100;

  const stats = [
    { value: total, label: "Total Plans" },
    { value: thisWeek, label: "This Week" },
    { value: failed, label: "Failed" },
    { value: `${successRate}%`, label: "Success Rate" },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      {stats.map((s) => (
        <div
          key={s.label}
          className="rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-950"
        >
          <p className="text-2xl font-bold text-zinc-900 dark:text-zinc-50">{s.value}</p>
          <p className="mt-1 text-xs text-zinc-500">{s.label}</p>
        </div>
      ))}
    </div>
  );
}

export function PlansView() {
  const [allPlans, setAllPlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [skip, setSkip] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const loadPlans = useCallback(
    async (nextSkip: number) => {
      setLoading(true);
      const result = await fetchPlans(nextSkip, PAGE_SIZE);
      if (result.success) {
        setAllPlans((prev) =>
          nextSkip === 0 ? result.data : [...prev, ...result.data]
        );
        setHasMore(result.data.length === PAGE_SIZE);
        setError(null);
      } else {
        setError(result.error);
      }
      setLoading(false);
    },
    []
  );

  useEffect(() => {
    loadPlans(0);
  }, [loadPlans]);

  const filtered = useMemo(() => {
    let list = allPlans;
    if (statusFilter) list = list.filter((p) => p.status === statusFilter);
    if (search) {
      const q = search.toLowerCase();
      list = list.filter(
        (p) =>
          p.intent_type.toLowerCase().includes(q) ||
          p.id.toLowerCase().includes(q)
      );
    }
    return list;
  }, [allPlans, statusFilter, search]);

  return (
    <div className="mx-auto max-w-4xl space-y-6 px-4 py-8 sm:px-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">Plans</h1>
        <FilterBar
          search={search}
          status={statusFilter}
          onSearchChange={setSearch}
          onStatusChange={setStatusFilter}
        />
      </div>

      {loading && allPlans.length === 0 ? (
        <>
          <StatsCardSkeleton cards={4} />
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <PlanCardSkeleton key={i} />
            ))}
          </div>
        </>
      ) : error && allPlans.length === 0 ? (
        <div className="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-300">
          Failed to load plans: {error}
        </div>
      ) : (
        <>
          <StatsCards plans={allPlans} />

          {filtered.length === 0 ? (
            <p className="py-8 text-center text-sm text-zinc-500">
              No plans match your filters.
            </p>
          ) : (
            <div className="space-y-4">
              {filtered.map((plan) => (
                <PlanCard key={plan.id} plan={plan} />
              ))}
            </div>
          )}

          {hasMore && !search && !statusFilter && (
            <div className="text-center">
              <button
                onClick={() => {
                  const next = skip + PAGE_SIZE;
                  setSkip(next);
                  loadPlans(next);
                }}
                disabled={loading}
                className="min-h-[44px] rounded-xl border border-zinc-200 bg-white px-6 py-2 text-sm font-semibold text-zinc-700 shadow-sm transition hover:bg-zinc-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 disabled:opacity-50 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-200"
              >
                {loading ? "Loading..." : "Load more"}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
