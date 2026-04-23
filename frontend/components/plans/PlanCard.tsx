"use client";

import Link from "next/link";
import { useState } from "react";
import type { Plan } from "@/lib/plans/types";
import { StatusBadge } from "./StatusBadge";
import { TaskProgressBar } from "./TaskProgressBar";

function formatDate(iso: string) {
  return new Date(iso).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function durationSeconds(start: string, end: string | null) {
  if (!end) return null;
  const ms = new Date(end).getTime() - new Date(start).getTime();
  return (ms / 1000).toFixed(1) + "s";
}

type Props = { plan: Plan };

export function PlanCard({ plan }: Props) {
  const [expanded, setExpanded] = useState(false);

  const completedTasks = Object.values(plan.task_status).filter(
    (s) => s === "completed"
  ).length;
  const totalTasks = plan.tasks?.length ?? Object.keys(plan.task_status).length;
  const duration = durationSeconds(plan.created_at, plan.completed_at);

  return (
    <div className="overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
      <div className="p-5">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-base" aria-hidden>📋</span>
              <Link
                href={`/plans/detail?id=${encodeURIComponent(plan.id)}`}
                className="truncate font-mono text-xs font-semibold text-zinc-500 hover:text-zinc-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:hover:text-zinc-50"
              >
                Plan #{plan.id.slice(0, 8)}
              </Link>
            </div>
            <p className="mt-1 text-sm font-semibold text-zinc-900 dark:text-zinc-50">
              {plan.intent_type.replace(/_/g, " ")}
            </p>
            <p className="mt-0.5 text-xs text-zinc-500">
              {formatDate(plan.created_at)}
              {duration && <> · {duration}</>}
            </p>
          </div>
          <StatusBadge status={plan.status} />
        </div>

        {totalTasks > 0 && (
          <div className="mt-4">
            <TaskProgressBar completed={completedTasks} total={totalTasks} />
          </div>
        )}

        <div className="mt-3 flex items-center gap-3">
          <button
            onClick={() => setExpanded((e) => !e)}
            className="text-xs font-semibold text-zinc-500 hover:text-zinc-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:hover:text-zinc-50"
            aria-expanded={expanded}
          >
            {expanded ? "Hide tasks ▲" : "Show tasks ▼"}
          </button>
          <Link
            href={`/plans/detail?id=${encodeURIComponent(plan.id)}`}
            className="text-xs font-semibold text-zinc-500 hover:text-zinc-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:hover:text-zinc-50"
          >
            View details →
          </Link>
        </div>
      </div>

      {expanded && plan.tasks && plan.tasks.length > 0 && (
        <div className="border-t border-zinc-100 bg-zinc-50 px-5 py-4 dark:border-zinc-800 dark:bg-zinc-900">
          <ul className="space-y-2">
            {plan.tasks.map((task) => (
              <li key={task.id} className="flex items-start gap-2 text-xs">
                <span aria-hidden className="mt-0.5 shrink-0">
                  {task.status === "completed"
                    ? "✅"
                    : task.status === "failed"
                    ? "❌"
                    : task.status === "running"
                    ? "⏳"
                    : "⏸"}
                </span>
                <span className="text-zinc-700 dark:text-zinc-300">
                  {task.description}
                  {task.status === "failed" && task.error && (
                    <span className="ml-1 text-red-600 dark:text-red-400">
                      — {task.error}
                    </span>
                  )}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
