import Link from "next/link";
import type { RecentPlan } from "@/lib/dashboard/types";
import { StatusBadge } from "@/components/plans/StatusBadge";

function relativeTime(iso: string) {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

type Props = { plans: RecentPlan[] };

export function RecentPlansList({ plans }: Props) {
  if (plans.length === 0) {
    return (
      <p className="py-4 text-center text-sm text-zinc-400">No plans yet.</p>
    );
  }

  return (
    <ul className="divide-y divide-zinc-100 dark:divide-zinc-800">
      {plans.map((plan) => (
        <li key={plan.id}>
          <Link
            href={`/plans/detail?id=${encodeURIComponent(plan.id)}`}
            className="flex items-center gap-3 py-3 hover:bg-zinc-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-400 dark:hover:bg-zinc-900"
          >
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium capitalize text-zinc-800 dark:text-zinc-200">
                {plan.intent_type.replace(/_/g, " ")}
              </p>
              <p className="font-mono text-xs text-zinc-400">
                #{plan.id.slice(0, 8)} · {relativeTime(plan.created_at)}
              </p>
            </div>
            <StatusBadge status={plan.status} showIcon={false} />
          </Link>
        </li>
      ))}
    </ul>
  );
}
