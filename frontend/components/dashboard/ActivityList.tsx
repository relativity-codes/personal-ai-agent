import type { ActivityItem } from "@/lib/dashboard/types";

function relativeTime(iso: string) {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

type Props = { items: ActivityItem[] };

export function ActivityList({ items }: Props) {
  if (items.length === 0) {
    return (
      <p className="py-4 text-center text-sm text-zinc-400">No recent activity.</p>
    );
  }

  return (
    <ul className="divide-y divide-zinc-100 dark:divide-zinc-800">
      {items.map((item) => (
        <li key={item.id} className="flex items-start gap-3 py-3">
          <span
            className="mt-0.5 text-sm"
            aria-label={item.success ? "success" : "failed"}
          >
            {item.success ? "✅" : "❌"}
          </span>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-zinc-800 dark:text-zinc-200">
              {item.intent_type
                ? item.intent_type.replace(/_/g, " ")
                : item.action}
            </p>
            <p className="text-xs text-zinc-400">{relativeTime(item.created_at)}</p>
          </div>
          {item.execution_time_ms && (
            <span className="shrink-0 text-xs text-zinc-400">
              {(item.execution_time_ms / 1000).toFixed(1)}s
            </span>
          )}
        </li>
      ))}
    </ul>
  );
}
