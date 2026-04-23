import type { PlanTask } from "@/lib/plans/types";

type Props = { tasks: PlanTask[] };

const STATUS_COLORS: Record<string, string> = {
  completed: "border-emerald-400 bg-emerald-50 dark:bg-emerald-950",
  failed: "border-red-400 bg-red-50 dark:bg-red-950",
  running: "border-blue-400 bg-blue-50 dark:bg-blue-950",
  pending: "border-zinc-300 bg-zinc-50 dark:bg-zinc-900",
};

const STATUS_ICONS: Record<string, string> = {
  completed: "✅",
  failed: "❌",
  running: "⏳",
  pending: "⏸",
};

export function TaskDependencyGraph({ tasks }: Props) {
  if (tasks.length === 0) return null;

  const sorted = [...tasks].sort((a, b) => a.step - b.step);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
      <h2 className="mb-4 text-sm font-semibold text-zinc-900 dark:text-zinc-50">
        Task Dependency Graph
      </h2>
      <div className="overflow-x-auto">
        <div className="flex min-w-max flex-col gap-3">
          {sorted.map((task, i) => (
            <div key={task.id} className="flex items-center gap-3">
              <div
                className={[
                  "w-56 shrink-0 rounded-xl border-2 px-3 py-2 text-xs",
                  STATUS_COLORS[task.status] ?? STATUS_COLORS.pending,
                ].join(" ")}
              >
                <div className="flex items-center gap-1.5">
                  <span aria-hidden>{STATUS_ICONS[task.status] ?? "⏸"}</span>
                  <span className="font-semibold text-zinc-800 dark:text-zinc-200">
                    Task {task.step}
                  </span>
                  <span className="ml-auto font-mono text-zinc-400">{task.mcp_server}</span>
                </div>
                <p className="mt-0.5 truncate text-zinc-600 dark:text-zinc-400">
                  {task.description}
                </p>
              </div>

              {task.depends_on && task.depends_on.length > 0 && (
                <div className="flex items-center gap-1 text-xs text-zinc-400">
                  <span aria-hidden>←</span>
                  <span>depends on step {task.depends_on.join(", ")}</span>
                </div>
              )}

              {i < sorted.length - 1 && (
                <div
                  className="ml-auto h-px w-6 bg-zinc-300 dark:bg-zinc-700"
                  aria-hidden
                />
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
