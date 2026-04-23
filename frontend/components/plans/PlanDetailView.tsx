"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { PlanCardSkeleton } from "@/components/shared/loading/PlanCardSkeleton";
import { fetchPlanStatus } from "@/lib/plans/api";
import { sendMessageRest } from "@/lib/chat/websocket";
import type { PlanStatusResponse } from "@/lib/plans/types";
import { PlanHeader } from "./PlanHeader";
import { RawJsonViewer } from "./RawJsonViewer";
import { TaskDependencyGraph } from "./TaskDependencyGraph";
import { TaskDetail } from "./TaskDetail";

type Props = { planId: string };

export function PlanDetailView({ planId }: Props) {
  const router = useRouter();
  const [plan, setPlan] = useState<PlanStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    const result = await fetchPlanStatus(planId);
    if (result.success) {
      setPlan(result.data);
      setError(null);
    } else {
      setError(result.error);
    }
    setLoading(false);
  }, [planId]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleRetry() {
    if (!plan) return;
    try {
      const result = await sendMessageRest(plan.intent.replace(/_/g, " "));
      router.push(`/chat?session_id=${result.session_id}`);
    } catch {
      router.push("/chat");
    }
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl space-y-4 px-4 py-8 sm:px-6">
        <PlanCardSkeleton className="h-48" />
        <PlanCardSkeleton className="h-64" />
        <PlanCardSkeleton />
      </div>
    );
  }

  if (error || !plan) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6">
        <div className="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-300">
          {error ?? "Plan not found."}
        </div>
        <Link
          href="/plans"
          className="mt-4 inline-block text-sm font-semibold text-zinc-700 hover:text-zinc-900 dark:text-zinc-300 dark:hover:text-zinc-50"
        >
          ← Back to Plans
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6 px-4 py-8 sm:px-6">
      <Link
        href="/plans"
        className="inline-block text-xs font-semibold text-zinc-500 hover:text-zinc-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:hover:text-zinc-50"
      >
        ← All Plans
      </Link>

      <PlanHeader plan={plan} onRetry={handleRetry} />

      {plan.tasks && plan.tasks.length > 0 && (
        <TaskDependencyGraph tasks={plan.tasks} />
      )}

      {plan.tasks && plan.tasks.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">
            Task Details
          </h2>
          {plan.tasks.map((task) => (
            <TaskDetail
              key={task.id}
              task={task}
              result={plan.task_results?.[task.id]}
            />
          ))}
        </div>
      )}

      <RawJsonViewer data={plan} />
    </div>
  );
}
