"use client";

import { useState } from "react";
import type { PlanTask } from "@/lib/plans/types";
import { StatusBadge } from "./StatusBadge";

type Props = { task: PlanTask; result: unknown };

export function TaskDetail({ task, result }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <div className="overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center justify-between gap-3 p-5 text-left focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400"
        aria-expanded={open}
      >
        <div className="flex items-center gap-3">
          <StatusBadge status={task.status} />
          <span className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">
            Task {task.step}: {task.description}
          </span>
        </div>
        <span className="text-xs text-zinc-400">{open ? "▲" : "▼"}</span>
      </button>

      {open && (
        <div className="border-t border-zinc-100 bg-zinc-50 p-5 dark:border-zinc-800 dark:bg-zinc-900">
          <dl className="space-y-3 text-xs">
            <div className="flex gap-4">
              <dt className="w-24 shrink-0 font-semibold text-zinc-500">MCP Server</dt>
              <dd className="font-mono text-zinc-800 dark:text-zinc-200">{task.mcp_server}</dd>
            </div>
            <div className="flex gap-4">
              <dt className="w-24 shrink-0 font-semibold text-zinc-500">Tool</dt>
              <dd className="font-mono text-zinc-800 dark:text-zinc-200">{task.tool}</dd>
            </div>
            <div>
              <dt className="mb-1 font-semibold text-zinc-500">Parameters</dt>
              <dd>
                <pre className="overflow-x-auto rounded-xl bg-zinc-100 p-3 font-mono text-xs text-zinc-800 dark:bg-zinc-800 dark:text-zinc-200">
                  {JSON.stringify(task.parameters, null, 2)}
                </pre>
              </dd>
            </div>
            {result !== undefined && result !== null && (
              <div>
                <dt className="mb-1 font-semibold text-zinc-500">Result</dt>
                <dd>
                  <pre className="overflow-x-auto rounded-xl bg-zinc-100 p-3 font-mono text-xs text-zinc-800 dark:bg-zinc-800 dark:text-zinc-200">
                    {JSON.stringify(result, null, 2)}
                  </pre>
                </dd>
              </div>
            )}
            {task.error && (
              <div>
                <dt className="mb-1 font-semibold text-red-600 dark:text-red-400">Error</dt>
                <dd className="rounded-xl bg-red-50 p-3 text-xs text-red-700 dark:bg-red-950 dark:text-red-300">
                  {task.error}
                </dd>
              </div>
            )}
          </dl>
        </div>
      )}
    </div>
  );
}
