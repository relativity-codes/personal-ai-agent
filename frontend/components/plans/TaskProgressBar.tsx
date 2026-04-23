type Props = {
  completed: number;
  total: number;
};

export function TaskProgressBar({ completed, total }: Props) {
  const pct = total > 0 ? Math.round((completed / total) * 100) : 0;
  return (
    <div className="flex items-center gap-2">
      <div
        className="h-1.5 flex-1 overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800"
        role="progressbar"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`${completed} of ${total} tasks completed`}
      >
        <div
          className="h-full rounded-full bg-zinc-900 transition-all dark:bg-zinc-50"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="shrink-0 text-xs text-zinc-500">
        {completed}/{total}
      </span>
    </div>
  );
}
