/** §3.3 Plan card loading — shimmer panel. */
export function PlanCardSkeleton({ className }: { className?: string }) {
  return (
    <div
      className={[
        "relative overflow-hidden rounded-2xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950",
        className ?? "h-40",
      ].join(" ")}
      aria-hidden
    >
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/50 to-transparent dark:via-white/10 animate-plan-shimmer" />
      <div className="relative space-y-3 p-5 opacity-40">
        <div className="h-4 w-2/3 max-w-xs rounded bg-zinc-300 dark:bg-zinc-700" />
        <div className="h-3 w-1/2 max-w-[200px] rounded bg-zinc-300 dark:bg-zinc-700" />
        <div className="h-3 w-full max-w-md rounded bg-zinc-300 dark:bg-zinc-700" />
      </div>
    </div>
  );
}
