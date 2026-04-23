"use client";

import type { PlanStatusResponse } from "@/lib/plans/types";
import { StatusBadge } from "./StatusBadge";

function formatDate(iso: string) {
  return new Date(iso).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function durationSeconds(start: string, end: string | null) {
  if (!end) return null;
  const ms = new Date(end).getTime() - new Date(start).getTime();
  return (ms / 1000).toFixed(1) + " seconds";
}

type Props = {
  plan: PlanStatusResponse;
  onRetry: () => void;
};

export function PlanHeader({ plan, onRetry }: Props) {
  const duration = durationSeconds(plan.created_at, plan.completed_at);
  const completedCount = Object.values(plan.task_status).filter(
    (s) => s === "completed"
  ).length;
  const totalCount = Object.keys(plan.task_status).length;
  const successRate =
    totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 100;

  function handleExport() {
    const blob = new Blob([JSON.stringify(plan, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `plan-${plan.plan_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function handleShare() {
    navigator.clipboard.writeText(window.location.href).catch(() => {});
  }

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <StatusBadge status={plan.status} />
            <span className="font-mono text-xs text-zinc-400">
              {plan.plan_id}
            </span>
          </div>
          <p className="text-base font-semibold capitalize text-zinc-900 dark:text-zinc-50">
            {plan.intent.replace(/_/g, " ")}
          </p>
        </div>
        <p className="text-sm font-semibold text-zinc-500">
          Success rate: {successRate}%
        </p>
      </div>

      <dl className="mt-4 grid grid-cols-2 gap-x-6 gap-y-2 text-xs sm:grid-cols-3">
        <div>
          <dt className="text-zinc-400">Created</dt>
          <dd className="font-medium text-zinc-700 dark:text-zinc-300">
            {formatDate(plan.created_at)}
          </dd>
        </div>
        {plan.completed_at && (
          <div>
            <dt className="text-zinc-400">Completed</dt>
            <dd className="font-medium text-zinc-700 dark:text-zinc-300">
              {formatDate(plan.completed_at)}
            </dd>
          </div>
        )}
        {duration && (
          <div>
            <dt className="text-zinc-400">Duration</dt>
            <dd className="font-medium text-zinc-700 dark:text-zinc-300">{duration}</dd>
          </div>
        )}
      </dl>

      <div className="mt-5 flex flex-wrap gap-2">
        <button
          onClick={onRetry}
          className="min-h-[44px] rounded-xl border border-zinc-200 bg-white px-4 py-2 text-sm font-semibold text-zinc-700 shadow-sm transition hover:bg-zinc-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-200 dark:hover:bg-zinc-900"
        >
          Retry
        </button>
        <button
          onClick={handleExport}
          className="min-h-[44px] rounded-xl border border-zinc-200 bg-white px-4 py-2 text-sm font-semibold text-zinc-700 shadow-sm transition hover:bg-zinc-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-200 dark:hover:bg-zinc-900"
        >
          Export JSON
        </button>
        <button
          onClick={handleShare}
          className="min-h-[44px] rounded-xl border border-zinc-200 bg-white px-4 py-2 text-sm font-semibold text-zinc-700 shadow-sm transition hover:bg-zinc-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-200 dark:hover:bg-zinc-900"
        >
          Copy link
        </button>
      </div>
    </div>
  );
}
