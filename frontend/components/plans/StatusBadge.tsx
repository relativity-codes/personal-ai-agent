import type { PlanStatus } from "@/lib/plans/types";

const CONFIG: Record<PlanStatus, { label: string; classes: string }> = {
  completed: {
    label: "Completed",
    classes:
      "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950 dark:text-emerald-300 dark:border-emerald-800",
  },
  failed: {
    label: "Failed",
    classes:
      "bg-red-50 text-red-700 border-red-200 dark:bg-red-950 dark:text-red-300 dark:border-red-800",
  },
  running: {
    label: "In Progress",
    classes:
      "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950 dark:text-blue-300 dark:border-blue-800",
  },
  pending: {
    label: "Pending",
    classes:
      "bg-zinc-100 text-zinc-600 border-zinc-200 dark:bg-zinc-800 dark:text-zinc-400 dark:border-zinc-700",
  },
};

const ICONS: Record<PlanStatus, string> = {
  completed: "✅",
  failed: "❌",
  running: "⏳",
  pending: "⏸",
};

type Props = {
  status: PlanStatus | string;
  showIcon?: boolean;
};

export function StatusBadge({ status, showIcon = true }: Props) {
  const key = (status as PlanStatus) in CONFIG ? (status as PlanStatus) : "pending";
  const cfg = CONFIG[key];
  return (
    <span
      className={[
        "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-semibold",
        cfg.classes,
      ].join(" ")}
    >
      {showIcon && <span aria-hidden>{ICONS[key]}</span>}
      {cfg.label}
    </span>
  );
}
